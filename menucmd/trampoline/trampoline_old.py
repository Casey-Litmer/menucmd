from macrolibs.typemacros import maybe_arg, tupler;
from menucmd import Menu
from dataclasses import dataclass, field;
from collections import deque;
from typing import Any, Callable, List;
from .global_objs import MenuEscape;
from ..src.result import Result;
from ..src.bind import Bind;


__null__ = type('__null__', (object,), {});

#==================================================================================

@dataclass
class StackItem:
    manager: Any | None = None
    menu: Menu | None = None
    func: Callable = lambda x: x
    args: tuple[Any, ...] = ()

    def __str__(self):
        return f'(\n\
    manager: {self.manager} \n\
    menu: {self.menu.name} \n\
    func: {self.func} \n\
    args: {self.args} \n\
)'
    
@dataclass
class MenuScope:
    menu: Any | None = None
    results: List[Any] = field(default_factory=list)
    stack_size: int = 0

    def __str__(self):
        return f'(\n\
    menu: {self.menu.name} \n\
    results: {self.results} \n\
    stack_size: {self.stack_size} \n\
)'

#==================================================================================
class MenuManager:
    active_instance = None;
    __null__ = __null__;      # Tells the manager not to append a result

    def __init__(self):
        self.callstack: deque[StackItem] = deque();
        self.menu_scopes: deque[StackItem] = deque();
        self.running = False;   
        self.output = None;     # Sends last result between scopes and out the top menu
    
    #==================================================================================
    @staticmethod
    def manage_call(menu, arg, selection):
        if not MenuManager.active_instance:
            MenuManager.active_instance = MenuManager();
        return MenuManager.active_instance.enqueue_menu(menu, arg, selection);

    #==================================================================================
    def enqueue_menu(self, menu, arg, selection):
        """Adds a new menu scope and selected function chain to the callstack"""
        # Create New Menu Scope
        new_scope = MenuScope(menu=menu);
        self.menu_scopes.append(new_scope);

        # New stack to add to begnning
        new_stack = deque();

        # Append Exit
        if selection == menu.exit_key:
            #Enqueue exit_to
            def exit_to():
                self.exit_menu_scope();
                res = maybe_arg(menu.exit_to)(arg); 
                return res; 
            self.append_stack(new_stack, new_scope, menu, exit_to, ());
        
        # Append Invalid Selection
        elif selection not in menu.menu.keys():
            #Enqueue invalid selection
            def invalid_selection():
                print("--*Invalid Selection*--");
                self.exit_menu_scope();
                res = menu(arg);
                return res;
            self.append_stack(new_stack, new_scope, menu, invalid_selection, ());

        # Construct function chain
        else:    
            # Get User Selection
            chain = menu.menu[selection];
        
            # Enqueue arg_to
            self.append_stack(new_stack, new_scope, menu, maybe_arg(menu.arg_to), (arg,));
        
            # Enqueue function chain
            while len(chain) >= 2:
                func = chain[0];
                args = tupler(chain[1]);
                self.append_stack(new_stack, new_scope, menu, func, args);
                chain = chain[2:]

                # Enqueue escape_to
                def escape_to(result):
                    if result is MenuEscape:
                        self.exit_menu_scope();
                        res = maybe_arg(menu.escape_to)(arg);
                        return res;
                    return MenuManager.__null__;
                self.append_stack(new_stack, new_scope, menu, escape_to, (Result(-1),));
        
        # Enqueue end_to
        def end_to(result):
            self.exit_menu_scope();
            res = result if result is not None else maybe_arg(menu.end_to)(arg);
            return res;
        self.append_stack(new_stack, new_scope, menu, end_to, (Result(-1),));

        # Push new menu stack to front
        self.callstack = new_stack + self.callstack;
    
        # Run stack
        if not self.running:
            self.running = True;
            self.run_stack();
            return self.output;

        # Pipes through if already in loop
        return MenuManager.__null__;

    #==================================================================================
    def run_stack(self):
        """Main Evaluation Loop"""
        while self.callstack:
            # Get Current Scope
            current_scope = self.menu_scopes[-1];
            results = current_scope.results;

            # Pop From Stack
            item = self.callstack.popleft();
            menu, func, args = item.menu, item.func, item.args;
            current_scope.stack_size -= 1;

            # Replace Results and Separate args/kwargs
            func, args, kwargs = menu.replace_keywords(func, args, results)
    
            # Evaluate Function
            result = Bind.lazy_eval(func, args, kwargs);

            # Get Current Scope (possibly updated)
            if len(self.menu_scopes):
                current_scope = self.menu_scopes[-1];

            # End Loop
            self.append_result(current_scope, result);

        # Terminate MenuManager Instance
        self.running = False;
        MenuManager.active_instance = None;

    #==================================================================================
    def append_stack(self, new_stack: deque[StackItem], scope: MenuScope, menu, func, args):
        """Adds function to stack and informs the scope"""
        new_stack.append(StackItem(manager=self, menu=menu, func=func, args=args));
        scope.stack_size += 1;

    def append_result(self, scope: MenuScope, result: Any):
        """Appends the result to a scope's results and updates the manager output"""
        if result is not MenuManager.__null__:
            scope.results.append(result);
            self.output = result;

    def exit_menu_scope(self):
        """Exits a scope and purges the callstack of the scope's remaining items"""
        if len(self.menu_scopes):
            # Remove Scope
            current_scope = self.menu_scopes.pop();
            
            # Remove remaining calls of the scope
            for _ in range(current_scope.stack_size):
                self.callstack.popleft();

            # Append exited scope's return to last scope
            if self.menu_scopes:
                self.append_result(self.menu_scopes[-1], self.output);

                #Remove all unused and escaped scopes                                                              
                #if prev_stack_size <= 0: #or prev_scope_results[-1] == MenuEscape: 
                #    self.exit_menu_scope(result);