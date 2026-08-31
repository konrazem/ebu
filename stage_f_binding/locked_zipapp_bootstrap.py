import builtins,ctypes,hashlib,json,os,re,runpy,sys,time

class BootstrapRefusal(RuntimeError): pass

_SHA=re.compile(r"^[0-9a-f]{64}$")
_PATH=re.compile(r"^\\\\\?\\Volume\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}\\[^/:\\]+(?<![. ])(?:\\[^/:\\]+(?<![. ]))*$")
_IH=ctypes.c_void_p(-1).value
_AO=("--validator-zipapp","--validator-zipapp-byte-count","--validator-zipapp-sha256")
_DO=_AO+("--host-runtime-lock-acquisition-sha256","--durability-probe-phase","--invocation-preimage")
_PO=("--restart-challenge","--restart-challenge-sha256","--write-acknowledgement")
_SO="--locked-validator-subcommand"; _SC=("control-state","source-artifacts","durability-receipt","readiness-chain","record-chain")
_SN="_EBU_STAGE_F_LOCKED_ZIPAPP_V1"; _LS="_EBU_STAGE_F_BOOTSTRAP_LOCK_EVIDENCE_V1"; _LR=None

class _I(ctypes.Structure): _fields_=(('V',ctypes.c_uint64),('F',ctypes.c_ubyte*16))
class _S(ctypes.Structure): _fields_=(('A',ctypes.c_int64),('E',ctypes.c_int64),('N',ctypes.c_uint32),('P',ctypes.c_ubyte),('D',ctypes.c_ubyte),('X',ctypes.c_ubyte*2))
class _A(ctypes.Structure): _fields_=(('A',ctypes.c_uint32),('R',ctypes.c_uint32))

def _refuse(message): raise BootstrapRefusal(message)
def _winerror(operation): return BootstrapRefusal(f"{operation}: Win32 {ctypes.get_last_error()}")
def _digest(value,label):
    if _SHA.fullmatch(value) is None: _refuse(f"bad SHA-256: {label}")
    return value
def _path(value,label):
    if _PATH.fullmatch(value) is None or "\\.\\" in value or "\\..\\" in value: _refuse(f"bad volume-GUID path: {label}")
    return value
def _artifact_values(argv):
    values=dict(zip(_AO,argv[1:6:2])); values["--validator-zipapp"]=_path(values["--validator-zipapp"],"validator ZIP")
    text=values["--validator-zipapp-byte-count"]
    if not text.isascii() or not text.isdecimal() or text.startswith("0"): _refuse("bad ZIP count")
    count=int(text)
    if not 0<count<(1<<64): _refuse("ZIP count range")
    values["--validator-zipapp-byte-count"]=count; values["--validator-zipapp-sha256"]=_digest(values["--validator-zipapp-sha256"],"validator ZIP")
    return values
def _parse_args(argv):
    if len(argv)>=8 and tuple(argv[:6:2])==_AO and argv[6]==_SO:
        if argv[7] not in _SC: _refuse("bad subcommand")
        values=_artifact_values(argv); values["_forward"]=[argv[7],*argv[8:]]; return values
    if len(argv) not in (12,18) or tuple(argv[:12:2])!=_DO: _refuse("bad argument vector")
    values=_artifact_values(argv); values.update(zip(_DO[3:],argv[7:12:2])); phase=values["--durability-probe-phase"]
    if phase not in ("ORCHESTRATOR","PRE_RESTART","POST_RESTART"): _refuse("bad probe phase")
    if len(argv)==18:
        if phase!="POST_RESTART" or tuple(argv[12::2])!=_PO: _refuse("bad POST suffix")
        values.update(zip(_PO,argv[13::2]))
    elif phase=="POST_RESTART": _refuse("POST suffix missing")
    values["--host-runtime-lock-acquisition-sha256"]=_digest(values["--host-runtime-lock-acquisition-sha256"],"host-runtime-lock"); values["--invocation-preimage"]=_path(values["--invocation-preimage"],"invocation preimage")
    if phase=="POST_RESTART":
        values["--restart-challenge"]=_path(values["--restart-challenge"],"restart challenge"); values["--restart-challenge-sha256"]=_digest(values["--restart-challenge-sha256"],"restart challenge"); values["--write-acknowledgement"]=_path(values["--write-acknowledgement"],"acknowledgement")
        if values["--restart-challenge"]==values["--write-acknowledgement"]: _refuse("path collision")
    return values
def _bind(dll,name,arguments,result):
    function=getattr(dll,name); function.argtypes=arguments; function.restype=result; return function
def _apis():
    if sys.platform!="win32": _refuse("Win32 required")
    dll=ctypes.WinDLL("kernel32",use_last_error=True); void,dword=ctypes.c_void_p,ctypes.c_uint32
    return (_bind(dll,"CreateFileW",(ctypes.c_wchar_p,dword,dword,void,dword,dword,void),void),_bind(dll,"GetFinalPathNameByHandleW",(void,ctypes.c_wchar_p,dword,dword),dword),_bind(dll,"GetFileInformationByHandleEx",(void,ctypes.c_int,void,dword),ctypes.c_int),_bind(dll,"ReadFile",(void,void,dword,ctypes.POINTER(dword),void),ctypes.c_int),_bind(dll,"CloseHandle",(void,),ctypes.c_int))
def _query(query,handle,info_class,value,label):
    if not query(handle,info_class,ctypes.byref(value),ctypes.sizeof(value)): raise _winerror(label)
def _open_and_verify(values):
    global _LR
    create,final_path,query,read,close=_apis(); path=values["--validator-zipapp"]; count_bound=values["--validator-zipapp-byte-count"]; digest_bound=values["--validator-zipapp-sha256"]
    handle=create(path,0x80000000,1,None,3,0x00200000,None); acquired=time.time_ns()
    if handle in (None,_IH): raise _winerror("CreateFileW")
    try:
        buffer=ctypes.create_unicode_buffer(32768); length=final_path(handle,buffer,32768,1)
        if not 0<length<32768 or buffer.value!=path: _refuse("held ZIP path differs")
        file_id,standard,attribute=_I(),_S(),_A(); _query(query,handle,18,file_id,"FileIdInfo"); _query(query,handle,1,standard,"FileStandardInfo"); _query(query,handle,9,attribute,"FileAttributeTagInfo")
        if standard.E!=count_bound or standard.A<standard.E or standard.N!=1 or standard.P or standard.D: _refuse("held ZIP standard info differs")
        if attribute.A&0x400 or attribute.R: _refuse("held ZIP is reparse")
        digest,observed=hashlib.sha256(),0; raw=ctypes.create_string_buffer(1024*1024)
        while True:
            count=ctypes.c_uint32()
            if not read(handle,raw,len(raw),ctypes.byref(count),None): raise _winerror("ReadFile")
            if count.value==0: break
            observed+=count.value
            if observed>count_bound: _refuse("ZIP read exceeds bound")
            digest.update(raw.raw[:count.value])
        if observed!=count_bound or digest.hexdigest()!=digest_bound: _refuse("ZIP count/hash differs")
        _LR={"s":"stage_f_locked_zipapp_raw/v1","h":int(handle),"p":buffer.value,"v":int(file_id.V),"f":bytes(file_id.F).hex(),"a":int(standard.A),"e":int(standard.E),"n":int(standard.N),"d":bool(standard.P),"i":bool(standard.D),"t":int(attribute.A),"g":int(attribute.R),"c":observed,"x":digest.hexdigest(),"o":acquired,"q":time.time_ns()}
    except BaseException:
        if not close(handle): raise _winerror("CloseHandle after refusal")
        raise
    return handle,close
def _write_lock(values,raw):
    path=values["--invocation-preimage"]+".bootstrap-lock.json"; data=json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8"); stream=open(path,"xb",buffering=0)
    try:
        offset=0
        while offset<len(data): offset+=stream.write(data[offset:])
        os.fsync(stream.fileno())
    finally: stream.close()
def main(argv=None):
    original=list(sys.argv[1:] if argv is None else argv); values=_parse_args(original); handle,close=_open_and_verify(values)
    if hasattr(builtins,_SN) or hasattr(builtins,_LS): close(handle); _refuse("sentinel exists")
    context=(object(),int(handle),values["--validator-zipapp"],values["--validator-zipapp-byte-count"],values["--validator-zipapp-sha256"]); lock_context=_LR
    setattr(builtins,_SN,context); setattr(builtins,_LS,lock_context); prior=sys.argv
    try:
        sys.argv=[values["--validator-zipapp"],*values.get("_forward",original)]; runpy.run_path(values["--validator-zipapp"],run_name="__main__")
    finally:
        sys.argv=prior; intact=getattr(builtins,_SN,None) is context and getattr(builtins,_LS,None) is lock_context
        if getattr(builtins,_SN,None) is context: delattr(builtins,_SN)
        if getattr(builtins,_LS,None) is lock_context: delattr(builtins,_LS)
        if lock_context is not None: lock_context["r"]=time.time_ns()
        closed=bool(close(handle)); closed_ns=time.time_ns()
        if not closed: raise _winerror("CloseHandle")
        if not intact: _refuse("sentinel changed")
        if lock_context is not None and "_forward" not in values:
            lock_context["k"]=closed_ns; _write_lock(values,lock_context)

if __name__=="__main__": main()
