import torch
import functools
import inspect
import types


EXCLUDED_METHOD_NAMES = {
    'isinstance', 
    'issubclass', 
    'setattr', 
    'callable', 
    'list', 
    'tuple', 
    'len',
    'unpack_dual',
}

ALLOWED_OPERATORS = {
    '__add__',
    '__radd__',
    '__iadd__',
    '__sub__',
    '__rsub__',
    '__isub__',
    '__mul__',
    '__rmul__',
    '__imul__',
    '__truediv__',
    '__rtruediv__',
    '__itruediv__',
    '__floordiv__',
    '__rfloordiv__',
    '__ifloordiv__',
    '__mod__',
    '__rmod__',
    '__imod__',
    '__pow__',
    '__rpow__',
    '__ipow__',
    '__matmul__',
    '__rmatmul__',
    '__imatmul__',
    '__neg__',
    '__pos__',
    '__abs__',
    '__getitem__',
    '__setitem__',
}

class TensorPatcher:
    def __init__(self, callback=None):
        self.ctx_callback = callback

        visited = set()
        self.hijackers = [
            hijacker
            for module in self._all_modules(torch)
            for hijacker in self._to_hijackers(module, visited)
            if hijacker.target_method_name not in EXCLUDED_METHOD_NAMES
        ]
    
    def __enter__(self):
        if self.ctx_callback is None:
            raise ValueError()
        
        self.set_callback(self.ctx_callback)

    def __exit__(self, *args, **kwargs):
        self.clear_callback()

    def set_callback(self, callback):
        """Add a callback to be invoked after tensor functions are called."""
        for hijacker in self.hijackers:
            def patch(*args, _hijacker, **kwargs):
                input_tensors = self._extract_tensors(args, kwargs)
                if type(_hijacker.original_func) == type(int.real):
                    result = _hijacker.original_func.__get__(args[0])
                else:
                    result = _hijacker.original_func(*args, **kwargs)
                output_tensors = self._extract_tensors_from_result(result)
                callback(_hijacker, input_tensors, output_tensors)
                return result

            if type(getattr(hijacker.target_object, hijacker.target_method_name)) == type(int.real):
                hijacker.hijack(property(functools.partial(patch, _hijacker=hijacker)))
            elif inspect.isclass(hijacker.target_object):
                hijacker.hijack(functools.partialmethod(patch, _hijacker=hijacker))
            else:
                hijacker.hijack(functools.partial(patch, _hijacker=hijacker))

    def clear_callback(self):
        """Remove a previously added callback."""
        for hijacker in self.hijackers:
            hijacker.unhijack()
    
    def _to_hijackers(self, module, visited=None):
        if visited == None:
            visited = set()
        
        hijackers = []
        stack = [module]

        while stack:
            hijackable = stack.pop()
            visited.add(id(hijackable))

            for name in dir(hijackable):
                if (name.startswith('__') or name.startswith('_') or name.endswith('_')) and name not in ALLOWED_OPERATORS:
                    continue

                try:
                    value = getattr(hijackable, name, None)
                except Exception:
                    continue
                
                if value is None:
                    continue

                if not callable(value) and not isinstance(value, type(int.real)):
                    continue

                if isinstance(value, types.ModuleType):
                    continue

                if id(value) in visited:
                    continue

                stack.append(value)
                if inspect.isclass(value):
                    continue

                hijacker = FunctionHijacker(hijackable, name)
                if not hijacker.validate_hijackability():
                    continue
                
                hijackers.append(hijacker)

        return hijackers
    
    def _all_modules(self, root_package):
        modules = [root_package]
        visited = set()
        stack = [root_package]

        while stack:
            module = stack.pop()
            visited.add(id(module))

            for name in dir(module):
                submodule = getattr(module, name)
                if id(submodule) in visited:
                    continue
                
                if not isinstance(submodule, types.ModuleType):
                    continue
                
                if not module.__name__.startswith(root_package.__name__):
                    continue

                stack.append(submodule)
                modules.append(submodule)
        
        return [module for module in modules if module.__name__.startswith(root_package.__name__)]

    def _extract_tensors(self, args, kwargs):
        """Extract all tensors from function arguments."""
        tensors = []
        tensors.extend(self._find_tensors_in_args(args))
        tensors.extend(self._find_tensors_in_args(kwargs.values()))
        return tensors

    def _extract_tensors_from_result(self, result):
        """Extract tensors from the function result."""
        if isinstance(result, torch.Tensor):
            return [result]
        elif isinstance(result, (list, tuple)):
            return [t for item in result for t in self._extract_tensors_from_result(item)]
        return []

    def _find_tensors_in_args(self, args):
        tensors = []
        for arg in args:
            if isinstance(arg, torch.Tensor):
                tensors.append(arg)
            elif isinstance(arg, (tuple, list)):
                tensors.extend(self._find_tensors_in_args(arg))
        return tensors


class FunctionHijacker:
    def __init__(self, target_object, target_method_name, requires_self=False):
        self.target_object = target_object
        self.target_method_name = target_method_name
        self.requires_self = requires_self
        self.new_func = None
        self.original_func = None

    def hijack(self, new_func):
        self.new_func = new_func
        self.original_func = getattr(self.target_object, self.target_method_name)
        setattr(self.target_object, self.target_method_name, self.new_func)

    def unhijack(self):
        if self.original_func is not None:
            setattr(self.target_object, self.target_method_name, self.original_func)
        
        self.new_func = None
        self.original_func = None

    def validate_hijackability(self):
        try:
            self.hijack(getattr(self.target_object, self.target_method_name))
            self.unhijack()
            return True
        except Exception:
            try:
                self.unhijack()
            except Exception:
                pass
            return False
