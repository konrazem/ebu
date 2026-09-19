"""One-time mechanical migration of prior editable chapters; no model imports."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / 'parts_ii_iii_revised'
# New chapter number -> preserved draft source. New 49 and 58 are authored separately.
ORDER = {
 33:('II',33),34:('II',34),35:('II',36),36:('II',35),37:('II',38),
 38:('II',37),39:('II',39),40:('II',41),41:('II',42),42:('II',40),
 43:('II',43),44:('II',44),45:('II',45),46:('II',46),47:('III',47),
 48:('III',48),50:('III',49),51:('III',50),52:('III',51),53:('III',52),
 54:('III',53),55:('III',54),56:('III',55),57:('III',56),59:('III',57),
 60:('III',58),61:('III',59),62:('III',60),
}
REPLACEMENTS = {
 'Part III returns to the old Definition 6.4 wording:':r'Chapter~\ref{ch:measurement} returns to the old Definition 6.4 wording:',
 'Part III\nturns these distinctions':r'The implementation chapters later in this volume turn these distinctions',
 'finite expansion of Chapter 37':r'finite expansion of Chapter~\ref{ch:force}',
 'division needs the distinct treatment in the next chapters.':r'division needs the distinct treatment of Chapters~\ref{ch:groups} and~\ref{ch:attribution}.',
 'authority, not a consequence of Chapter 42.':r'authority, not a consequence of Chapter~\ref{ch:attribution}.',
 'Chapter 44 derives':r'Chapter~\ref{ch:dissipation} derives',
 'bound. The original network and timestep proofs are preserved in Appendix\nH-II,': 'bound. The original network and timestep proofs follow as a historical reading in this chapter,',
 'world. Appendix H-II retains the original proof at its own scope.':'world. The historical reading in this chapter retains the original proof at its own scope.',
 'architecture described in Part III.':'architecture developed in the following chapters of this volume.',
 'Q-test and D-test counts in Appendix H-III':'Q-test and D-test counts in the historical readings',
 "Part II derives the continuous-time dissipation structure and its finite-step":r'Chapter~\ref{ch:dissipation} derives the continuous-time dissipation structure and its finite-step',
 'Appendix H-III reproduces original Chapters 53--59, covering D1--D10,':r'The historical readings in Chapters~\ref{ch:evidence-route} and~\ref{ch:evidence} preserve the original account of D1--D10,',
 'The three books now have':'The first two parts now have',
}

def main():
 (ROOT/'chapters').mkdir(exist_ok=True)
 for number,(part,oldnum) in ORDER.items():
  destination=ROOT/f'chapters/{number}.tex'
  if destination.exists():
   raise RuntimeError(f'Will not overwrite an edited manuscript: {destination}')
  body=(OLD/part/f'{oldnum}.tex').read_text()
  for a,b in REPLACEMENTS.items(): body=body.replace(a,b)
  # Stable labels, rather than hard-coded chapter numerals, support future edits.
  destination.write_text(body)
 source=(OLD/'sources.tex').read_text().replace(
  'sources of the explicitly marked historical appendices.',
  'sources of the explicitly marked historical readings integrated by subject.')
 source=source.replace('retained in each\nappendix','retained in each\nhistorical reading')
 (ROOT/'sources.tex').write_text(source)
 (ROOT/'migration.json').write_text(json.dumps(ORDER,indent=2)+'\n')
 print('Migrated 28 editable chapters; abbreviated drafts preserved unchanged.')

if __name__=='__main__': main()
