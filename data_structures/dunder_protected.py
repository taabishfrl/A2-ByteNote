import re

class DunderProtected:
    """
    Allows subclass code to access base-class __dunder attributes using their
    own __name, by remapping _SubClass__attr -> _DefiningClass__attr across MRO.
    Outside code using obj.__attr (no mangling) still fails as usual.
    """
    _DU_PTN = re.compile(r"^_([A-Za-z_]\w*)__([A-Za-z_]\w*)$")

    def __getattribute__(self, name):
        # Fast path: try normal lookup first
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass

        # Remap: _CurrentClass__attr -> _OwnerClass__attr if it exists
        m = DunderProtected._DU_PTN.match(name)
        if m:
            want_owner, attr = m.group(1), m.group(2)
            # Try every class in MRO as a potential owner of the dunder attr
            for cls in type(self).mro():
                mangled = f"_{cls.__name__}__{attr}"
                # Avoid infinite recursion by peeking into __dict__ directly
                objdict = object.__getattribute__(self, "__dict__")
                if mangled in objdict:
                    return objdict[mangled]
                # Also allow class-level attributes/descriptors
                clsdict = object.__getattribute__(cls, "__dict__")
                if mangled in clsdict:
                    return clsdict[mangled].__get__(self, type(self)) \
                        if hasattr(clsdict[mangled], "__get__") else clsdict[mangled]

        # Fall back to normal error
        raise AttributeError(f"{type(self).__name__!s} object has no attribute {name!r}")

    def __setattr__(self, name, value):
        # If it's a dunder-mangled name, try to map to an existing owner slot
        m = DunderProtected._DU_PTN.match(name)
        if m:
            _, attr = m.group(1), m.group(2)
            for cls in type(self).mro():
                mangled = f"_{cls.__name__}__{attr}"
                objdict = object.__getattribute__(self, "__dict__")
                if mangled in objdict:
                    objdict[mangled] = value
                    return
            # If no existing owner slot, default to current class's name
            # (keeps normal Python semantics for first assignment)
        # Defer to default behavior
        super().__setattr__(name, value)
