import pandas as pd

def add_to_clipboard( data ):
    dfCP=pd.DataFrame([data])
    dfCP.to_clipboard(index=False,header=False)
    print(  "*")
    print( f"*** Added some data to your clipboard: <{data}>")
    print( f"*   Just type in open CTRL+V ENTER, and you can see your results in finder.")
    print( f"*************************************************************************************************")
