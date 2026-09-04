#!/usr/bin/env python3
"""Bounded GetProducts collection and exact, offline replay of price evidence.

Live collection calls only STS GetCallerIdentity and Pricing GetProducts. SDK
credentials remain in memory. Raw responses, canonical preimages and request
IDs are preserved in exclusive local files; a failed run remains inspectable.
The price API does not promise future price validity: an accounting horizon
must be separately justified before a model can be made launch eligible.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import re
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / 'aws_c0_cost_runtime_retrieval_closure_correction_evidence_schema.json'
CONTRACT_PATH = ROOT / 'aws_c0_cost_runtime_retrieval_closure_correction_contract.json'
MAX_INTEGER = 9007199254740991
ACCOUNT = '623609441658'
ROLE_PREFIX = f'arn:aws:sts::{ACCOUNT}:assumed-role/EBU-C0-Operator-492a4f1/'
MAX_PAGES = 128
MAX_ITEMS = 10000
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
# Conservative physical conversion bounds: a billing month is at least 28
# days; using decimal GB also covers GiB billing for byte-denominated usage.
# Lambda uses the committed 256 MiB, which is verified before conversion.
MONTH_SECONDS_MIN = 28 * 86400
CONVERSIONS = {
    'SECOND': {'Hrs': Fraction(100, 3600), 'hour': Fraction(100, 3600),
               'Hours': Fraction(100, 3600), 'Keys': Fraction(100, MONTH_SECONDS_MIN)},
    'REQUEST': {'Requests': Fraction(100), 'Request': Fraction(100)},
    'TRANSITION': {'States': Fraction(100), 'StateTransitions': Fraction(100)},
    'INVOCATION': {'Requests': Fraction(100)},
    'MILLISECOND': {'Lambda-GB-Second': Fraction(100, 4000), 'GB-Seconds': Fraction(100, 4000)},
    'BYTE': {'GB': Fraction(100, 10**9), 'GigaBytes': Fraction(100, 10**9)},
    'GIB_SECOND': {'GB-Mo': Fraction(100 * 2**30, 10**9 * MONTH_SECONDS_MIN)},
    'BYTE_SECOND': {'GB-Mo': Fraction(100, 10**9 * MONTH_SECONDS_MIN)},
    'IOPS_SECOND': {'IOPS-Mo': Fraction(100, MONTH_SECONDS_MIN)},
    'MIBPS_SECOND': {'MBps-Mo': Fraction(100 * 2**20, 10**6 * MONTH_SECONDS_MIN),
                     'GiBps-mo': Fraction(100, 1024 * MONTH_SECONDS_MIN)},
}


class Refusal(ValueError):
    pass


def require(test, message):
    if not test:
        raise Refusal(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(kind, value):
    hashed = digest(canonical(value))
    return {'kind': kind, 'sha256': hashed, 'value': hashed}


def strict(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def forbidden(value):
        raise Refusal('floating JSON numbers are forbidden')
    return json.loads(raw, object_pairs_hook=pairs, parse_float=forbidden, parse_constant=forbidden)


def schema_check(value, definition):
    from jsonschema import Draft202012Validator, FormatChecker
    schema = strict(SCHEMA_PATH.read_bytes())
    validator = Draft202012Validator({'$defs': schema['$defs'], '$ref': '#/$defs/' + definition},
                                    format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda e: str(e.path))
    require(not errors, f'{definition}: ' + '; '.join(e.message for e in errors[:3]))


def utc(value):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', value), 'UTC timestamp required')
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def bounded(value, positive=False):
    require(type(value) is int and (1 if positive else 0) <= value <= MAX_INTEGER, 'bounded integer required')
    return value


def decimal_parts(value):
    require(isinstance(value, str) and re.fullmatch(r'\d+(?:\.\d+)?', value), 'invalid decimal price')
    left, _, right = value.partition('.')
    # Strip insignificant zeroes before enforcing the frozen integer bound.
    right = right.rstrip('0')
    return bounded(int(left + right)), len(right)


def save(directory, name, value):
    path = directory / name
    with path.open('xb') as stream:
        stream.write(canonical(value))
    path.chmod(0o600)
    return path


def request_for(service, attributes):
    require(isinstance(service, str) and re.fullmatch(r'[A-Za-z0-9]+', service), 'invalid service')
    require(type(attributes) is dict and attributes, 'explicit product filters required')
    require(all(isinstance(k, str) and isinstance(v, str) and v for k, v in attributes.items()), 'invalid filters')
    return {'ServiceCode': service, 'FormatVersion': 'aws_v1', 'MaxResults': 100,
            'Filters': [{'Type': 'TERM_MATCH', 'Field': k, 'Value': v} for k, v in sorted(attributes.items())]}


def collect_pages(fetch, request, caller, sink, *, max_pages=MAX_PAGES, max_items=MAX_ITEMS):
    """fetch(request) returns (parsed API body, raw body, AWS request id).

    Injected transports are for offline testing only. The CLI supplies the
    authenticated SDK transport after validating the exact constrained caller.
    """
    bounded(max_pages, True); bounded(max_items, True)
    require('NextToken' not in request, 'collection must begin at first page')
    pages, seen, count, token = [], set(), 0, None
    for index in range(max_pages):
        current = copy.deepcopy(request)
        if token is not None:
            current['NextToken'] = token
        body, raw, request_id = fetch(current)
        require(isinstance(raw, bytes) and len(raw) <= MAX_RESPONSE_BYTES, 'oversize response')
        require(strict(raw) == body, 'wire response and parsed body differ')
        require(isinstance(request_id, str) and request_id, 'AWS request id missing')
        require(body.get('FormatVersion') == 'aws_v1' and isinstance(body.get('PriceList'), list), 'invalid price page')
        require(all(isinstance(x, str) for x in body['PriceList']), 'invalid price-list members')
        outgoing = body.get('NextToken')
        require(outgoing is None or isinstance(outgoing, str) and outgoing, 'invalid next token')
        receipt = {'service': 'pricing', 'action': 'GetProducts',
                   'request_sha256': digest(canonical(current)), 'response_sha256': digest(canonical(body)),
                   'request_id': request_id, 'caller_identity': caller, 'observed_utc': now(),
                   'authentication_disposition': 'AWS_SIGV4_RESPONSE_BOUND'}
        schema_check(receipt, 'authenticated_api_receipt')
        page = {'request': current, 'response': body, 'wire_response_base64': base64.b64encode(raw).decode(),
                'wire_response_sha256': digest(raw), 'receipt': receipt, 'page_index': index}
        sink(page)  # Keep successful observations even when later pages fail.
        pages.append(page)
        count += len(body['PriceList'])
        require(count <= max_items, 'price item bound exceeded')
        if outgoing is None:
            return pages
        require(outgoing not in seen, 'repeated pagination token')
        seen.add(outgoing)
        token = outgoing
    raise Refusal('price page bound exceeded before terminal page')


def validate_pages(pages):
    require(isinstance(pages, list) and 0 < len(pages) <= MAX_PAGES, 'invalid page set')
    token, seen, products, first, caller = None, set(), [], None, None
    for index, page in enumerate(pages):
        request, response, receipt = page['request'], page['response'], page['receipt']
        require(page['page_index'] == index and request.get('NextToken') == token, 'broken pagination chain')
        base = {k: v for k, v in request.items() if k != 'NextToken'}
        first = base if first is None else first
        require(base == first, 'query changed across pages')
        schema_check(receipt, 'authenticated_api_receipt')
        caller = receipt['caller_identity'] if caller is None else caller
        require(receipt['caller_identity'] == caller, 'caller changed across pages')
        raw = base64.b64decode(page['wire_response_base64'], validate=True)
        require(len(raw) <= MAX_RESPONSE_BYTES and digest(raw) == page['wire_response_sha256'] and strict(raw) == response, 'wire receipt mismatch')
        require(receipt['service'] == 'pricing' and receipt['action'] == 'GetProducts', 'wrong receipt API')
        require(receipt['request_sha256'] == digest(canonical(request)) and receipt['response_sha256'] == digest(canonical(response)), 'canonical receipt mismatch')
        require(response.get('FormatVersion') == 'aws_v1', 'wrong response format')
        for raw_product in response['PriceList']:
            product = strict(raw_product)
            require(product['serviceCode'] == request['ServiceCode'], 'service mismatch')
            for f in request['Filters']:
                require(f['Type'] == 'TERM_MATCH', 'unsupported filter')
                actual = product['product'].get(f['Field'], product['product']['attributes'].get(f['Field']))
                require(actual == f['Value'], 'returned product violates filter')
            products.append((page, product))
        require(len(products) <= MAX_ITEMS, 'price item bound exceeded')
        token = response.get('NextToken')
        require((index == len(pages)-1) == (token is None), 'missing or premature terminal page')
        if token is not None:
            require(isinstance(token, str) and token and token not in seen, 'repeated/invalid token')
            seen.add(token)
    require(products, 'empty pricing result')
    require(len({p['product']['sku'] for _, p in products}) == len(products), 'duplicate SKU across pages')
    return products


def rate_row(dimension, unit, pages, conversion, valid_from, valid_until, product_filter=None):
    """Convert every OnDemand tier in a sealed exact product query.

    conversion maps each source unit to [numerator, denominator] for cents
    per target unit per source USD. It is sealed in the proof, never inferred
    from a rate description. Caller must validate the physical unit mapping.
    """
    require(utc(valid_from) < utc(valid_until), 'invalid rate validity window')
    require(unit in CONVERSIONS, 'unknown target unit')
    if unit == 'MILLISECOND':
        template = strict((ROOT / 'aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml').read_bytes())
        require(template['Resources']['FinalizerFunction']['Properties']['MemorySize'] == 256,
                'Lambda memory changed; conversion requires review')
    product_filter = product_filter or {}
    require(type(product_filter) is dict and all(isinstance(k, str) and isinstance(v, str) for k, v in product_filter.items()),
            'invalid sealed product filter')
    candidates, coordinates, excluded_skus = [], set(), []
    for page, product in validate_pages(pages):
        attributes = {**product['product']['attributes'], 'sku': product['product']['sku']}
        if any(attributes.get(k) != v for k, v in product_filter.items()):
            excluded_skus.append(product['product']['sku'])
            continue
        require(utc(product['publicationDate']) <= utc(page['receipt']['observed_utc']), 'future publication')
        terms = product['terms'].get('OnDemand', {})
        require(terms, 'no OnDemand offer')
        for term_code, term in sorted(terms.items()):
            require(term['sku'] == product['product']['sku'] and utc(term['effectiveDate']) <= utc(valid_from), 'offer not effective')
            for rate_code, rate in sorted(term['priceDimensions'].items()):
                require(rate['rateCode'] == rate_code and not rate.get('appliesTo'), 'conditional or inconsistent rate')
                source_unit = rate['unit']
                require(source_unit in conversion and set(rate['pricePerUnit']) == {'USD'}, 'unsupported unit/currency')
                n, d = conversion[source_unit]
                bounded(n, True); bounded(d, True)
                require(source_unit in CONVERSIONS[unit] and Fraction(n, d) == CONVERSIONS[unit][source_unit],
                        'unreviewed physical unit conversion')
                price, scale = decimal_parts(rate['pricePerUnit']['USD'])
                begin, begin_scale = decimal_parts(rate['beginRange'])
                require(begin_scale == 0, 'fractional tier cannot be represented')
                end = None
                if rate['endRange'] != 'Inf':
                    end, end_scale = decimal_parts(rate['endRange'])
                    require(end_scale == 0 and end > begin, 'invalid tier interval')
                coordinate = (product['product']['sku'], term_code, rate_code)
                require(coordinate not in coordinates, 'duplicate rate coordinate')
                coordinates.add(coordinate)
                candidates.append((page, product, term_code, rate_code, rate, price, scale, n, d, begin, end,
                                   Fraction(price * n, 10**scale * d)))
    require(candidates and len(candidates) <= 256, 'rate observation bound')
    # Every SKU/term/unit must cover from zero to infinity without gaps.
    groups = {}
    for c in candidates:
        groups.setdefault((c[1]['product']['sku'], c[2], c[4]['unit']), []).append((c[9], c[10]))
    for intervals in groups.values():
        cursor = 0
        for begin, end in sorted(intervals):
            require(cursor is not None and begin == cursor, 'tier gap/overlap')
            cursor = end
        require(cursor is None, 'unterminated tier coverage')
    selected = max(c[-1] for c in candidates)
    if selected.denominator > MAX_INTEGER:
        selected = Fraction((selected.numerator * MAX_INTEGER + selected.denominator - 1) // selected.denominator,
                            MAX_INTEGER)
    bounded(selected.numerator); bounded(selected.denominator, True)
    proof = {'schema': 'aws_c0_rate_upper_bound_proof/v1', 'dimension': dimension, 'unit': unit,
             'conversion': conversion, 'selection': 'MAX_ALL_ONDEMAND_TIERS_OF_COMPLETE_EXACT_QUERY',
             'product_filter': product_filter, 'excluded_skus': sorted(excluded_skus),
             'numerator_minor_units': selected.numerator, 'denominator_units': selected.denominator,
             'pages': [{'request_sha256': p['receipt']['request_sha256'],
                        'response_sha256': p['receipt']['response_sha256'],
                        'incoming_token_sha256': digest(p['request']['NextToken'].encode()) if p['request'].get('NextToken') else None,
                        'outgoing_token_sha256': digest(p['response']['NextToken'].encode()) if p['response'].get('NextToken') else None}
                       for p in pages],
             'tiers': [{'sku': c[1]['product']['sku'], 'term_code': c[2], 'rate_code': c[3],
                        'numerator': c[-1].numerator, 'denominator': c[-1].denominator} for c in candidates]}
    proof_id = identity('aws_c0_rate_upper_bound_proof/v1', proof)
    observations = []
    for page, product, term_code, rate_code, rate, price, scale, n, d, begin, end, _ in candidates:
        observation = {'schema': 'aws_c0_pricing_observation/v1', 'api_action': 'pricing:GetProducts',
            'request_canonical_json_base64': base64.b64encode(canonical(page['request'])).decode(),
            'response_canonical_json_base64': base64.b64encode(canonical(page['response'])).decode(),
            'request_sha256': page['receipt']['request_sha256'], 'response_sha256': page['receipt']['response_sha256'],
            'source_receipt': page['receipt'], 'service_code': product['serviceCode'], 'region': 'us-east-1',
            'offer_version': product['version'], 'sku': product['product']['sku'], 'term_code': term_code,
            'rate_code': rate_code, 'tier_begin_units': begin, 'tier_end_units': end, 'source_unit': rate['unit'],
            'source_currency': 'USD', 'source_price_integer': price, 'source_decimal_scale': scale,
            'conversion_numerator': n, 'conversion_denominator': d,
            'selected_rate_upper_bound_proof_identity': proof_id, 'observed_utc': page['receipt']['observed_utc'],
            'valid_from_utc': valid_from, 'valid_until_utc': valid_until,
            'authentication_disposition': 'AWS_PRICING_RESPONSE_AUTHENTICATED'}
        observation['identity'] = identity('aws_c0_pricing_observation/v1', observation)
        schema_check(observation, 'pricing_observation')
        observations.append(observation)
    row = {'dimension': dimension, 'unit': unit, 'numerator_minor_units': selected.numerator,
           'denominator_units': selected.denominator, 'pricing_observations': observations,
           'pricing_observation_identities': [o['identity'] for o in observations],
           'selected_rate_upper_bound_proof_identity': proof_id,
           'selected_rate_upper_bound_proof_canonical_json_base64': base64.b64encode(canonical(proof)).decode()}
    schema_check(row, 'rate_row')
    return row


def cost_model(rows, valid_from, valid_until, observed_utc, fixed_minor_units=0):
    contract = strict(CONTRACT_PATH.read_bytes())
    require([r['dimension'] for r in rows] == contract['resource_dimensions_in_order'], 'exact 22 dimensions/order required')
    require(utc(valid_from) < utc(valid_until) and utc(observed_utc) <= utc(valid_until), 'invalid model window')
    for row in rows:
        schema_check(row, 'rate_row')
        require(row['unit'] == contract['resource_dimension_units'][row['dimension']], 'dimension unit mismatch')
    defs = strict(SCHEMA_PATH.read_bytes())['$defs']
    model = {k: v['const'] for k, v in defs['common']['properties'].items() if 'const' in v}
    model.update(schema='aws_c0_cost_model/v2', record_class='NON_SCIENTIFIC_AWS_C0_CONTROL_EVIDENCE',
                 zero_science_counters={k: 0 for k in defs['zero_science_counters']['required']}, observed_utc=observed_utc,
                 currency='USD', valid_from_utc=valid_from, valid_until_utc=valid_until,
                 rounding_rule='CEIL_EACH_DIMENSION_THEN_SUM_FIXED', fixed_minor_units=bounded(fixed_minor_units),
                 integer_maximum=MAX_INTEGER, product_maximum=MAX_INTEGER, total_maximum=MAX_INTEGER,
                 rates=rows, list_price_bound_not_invoice=True,
                 pricing_observation_set_identity=identity('aws_c0_pricing_observation_set/v1',
                     [o for r in rows for o in r['pricing_observation_identities']]))
    schema_check(model, 'cost_model')
    return model


def maximum_cost(model, limits):
    schema_check(model, 'cost_model')
    require(set(limits) == {r['dimension'] for r in model['rates']}, 'resource limit dimensions mismatch')
    total = bounded(model['fixed_minor_units'])
    for row in model['rates']:
        units = bounded(limits[row['dimension']])
        product = units * bounded(row['numerator_minor_units'])
        require(product <= model['product_maximum'], 'cost product overflow')
        denominator = bounded(row['denominator_units'], True)
        total += (product + denominator - 1) // denominator
        require(total <= model['total_maximum'], 'cost total overflow')
    require(total <= 5000, 'aggregate USD 50 ceiling exceeded')
    return total


def validate_model(model, evidence):
    """Rebuild every row from raw receipts; reject merely well-shaped claims.

    evidence contains one query's pages and a reviewed unit conversion per
    dimension. Future validity is a separate prerequisite, not an API fact.
    """
    schema_check(model, 'cost_model')
    contract = strict(CONTRACT_PATH.read_bytes())
    require(list(evidence) == contract['resource_dimensions_in_order'], 'evidence dimension order mismatch')
    rows = []
    for dimension in contract['resource_dimensions_in_order']:
        item = evidence[dimension]
        require(set(item) in ({'pages', 'conversion'}, {'pages', 'conversion', 'product_filter'}), 'unknown evidence field')
        rows.append(rate_row(dimension, contract['resource_dimension_units'][dimension], item['pages'],
                             item['conversion'], model['valid_from_utc'], model['valid_until_utc'], item.get('product_filter')))
    expected = cost_model(rows, model['valid_from_utc'], model['valid_until_utc'],
                          model['observed_utc'], model['fixed_minor_units'])
    require(model == expected, 'cost model does not match replayed source rates and proofs')
    return expected


def live_collect(service, filters, output, *, session=None):
    import boto3
    from botocore.config import Config
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    # Default credential chain accepts the already authorized constrained
    # session. This entry point never assumes roles or logs into SSO itself.
    session = session or boto3.Session(region_name='us-east-1')
    config = Config(retries={'total_max_attempts': 1}, connect_timeout=10, read_timeout=30)
    caller = session.client('sts', config=config).get_caller_identity()
    require(caller['Account'] == ACCOUNT and caller['Arn'] == ROLE_PREFIX + 'AWS-C0-PREP-492a4f1', 'exact constrained preparation caller required')
    caller_id = identity('aws_c0_constrained_operator_session/v1', {k: caller[k] for k in ('Account', 'Arn', 'UserId')})
    save(output, 'caller.json', caller)
    client = session.client('pricing', config=config)
    captured = []
    def capture(http_response, parsed, **kwargs):
        captured.append((http_response.content, parsed))
    client.meta.events.register('after-call.pricing.GetProducts', capture)
    def fetch(request):
        captured.clear()
        response = client.get_products(**request)
        require(len(captured) == 1, 'one HTTP response required')
        raw, _ = captured[0]
        body = {k: v for k, v in response.items() if k != 'ResponseMetadata'}
        return body, raw, response['ResponseMetadata']['RequestId']
    pages = collect_pages(fetch, request_for(service, filters), caller_id,
                          lambda p: save(output, f'page-{p["page_index"]:04d}.json', p))
    validate_pages(pages)
    save(output, 'completion.json', {'schema': 'aws_c0_local_pricing_collection/v1',
         'page_count': len(pages), 'item_count': sum(len(p['response']['PriceList']) for p in pages),
         'page_sha256': [digest(canonical(p)) for p in pages], 'terminal': True})


def build_from_collections(spec, directory):
    contract = strict(CONTRACT_PATH.read_bytes())
    require([r['dimension'] for r in spec['rows']] == contract['resource_dimensions_in_order'], 'exact build specification order required')
    rows, evidence = [], {}
    for item in spec['rows']:
        relative = Path(item['collection'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'collection path escapes evidence directory')
        collection = directory / relative
        paths = sorted(collection.glob('page-*.json'))
        completion = strict((collection / 'completion.json').read_bytes())
        pages = [strict(p.read_bytes()) for p in paths]
        require(completion['terminal'] is True and completion['page_count'] == len(pages) and
                completion['page_sha256'] == [digest(canonical(p)) for p in pages], 'collection completion mismatch')
        dimension = item['dimension']
        conversion = item['conversion']
        row = rate_row(dimension, contract['resource_dimension_units'][dimension], pages, conversion,
                       spec['valid_from_utc'], spec['valid_until_utc'], item.get('product_filter'))
        rows.append(row)
        evidence[dimension] = {'pages': pages, 'conversion': conversion}
        if 'product_filter' in item:
            evidence[dimension]['product_filter'] = item['product_filter']
    model = cost_model(rows, spec['valid_from_utc'], spec['valid_until_utc'], spec['observed_utc'],
                       spec['fixed_minor_units'])
    validate_model(model, evidence)
    bound = maximum_cost(model, spec['resource_limits'])
    return model, evidence, bound


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--service')
    parser.add_argument('--filters', type=Path)
    parser.add_argument('--build-spec', type=Path)
    parser.add_argument('--evidence-dir', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.build_spec:
        require(args.evidence_dir is not None and args.service is None and args.filters is None, 'invalid offline build arguments')
        model, evidence, bound = build_from_collections(strict(args.build_spec.read_bytes()), args.evidence_dir)
        args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
        save(args.output, 'cost-model.json', model)
        save(args.output, 'pricing-evidence.json', evidence)
        save(args.output, 'cost-bound.json', {'bound_minor_units': bound, 'ceiling_minor_units': 5000,
                                           'disposition': 'LOCAL_CANDIDATE_VALIDITY_AND_RESOURCE_SCOPE_REVIEW_REQUIRED'})
    else:
        require(args.service is not None and args.filters is not None and args.evidence_dir is None, 'invalid live collection arguments')
        live_collect(args.service, strict(args.filters.read_bytes()), args.output)


if __name__ == '__main__':
    main()
