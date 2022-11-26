import importlib
import sys
import runpy

def dynamic_imp(name, pipName):
    
    # find_module method is used to find the module and return the path and description
    try:
        myModule = importlib.import_module(name)

    except ImportError:

        print('Module not found: '+name)
        sys.argv=['pip', 'install', pipName]
        runpy.run_module('pip', run_name='__main__')
        
        try:
            myModule=importlib.import_module(name)
        
        except ImportError:
            print('Unable to install module: '+name+' ('+pipName+')')
            exit()

    return myModule

if __name__=='__main__':
    pd=dynamic_imp('pandas', 'pandas')
    df=pd.DataFrame()
    print(df)
    dne=dynamic_imp('dne_module', 'dne')
