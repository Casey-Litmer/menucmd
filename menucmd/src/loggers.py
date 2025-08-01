import traceback;


logVCallstack = True
logScopes = True


#==================================================================================

def log_vcallstack(manager):
    if logVCallstack and manager.callstack and manager.menu_scopes:
        print('---------------------')
        #print(menu.name, '---', item)
        print('CALLSTACK')
        print('---------------------')
        for i in manager.callstack: print(i.menu.name, '---', i)

def log_scopes(manager):
    if logScopes and manager.callstack and manager.menu_scopes:
        print('-') 
        print('MENU SCOPES')
        print('-----------')
        for s in manager.menu_scopes: print(s.menu.name, '---', s)

def printStackStringLength():
    stack_str = ''.join(traceback.format_stack());
    print('callstack size:', len(stack_str));