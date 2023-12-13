class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def Error( variable, message = "" ):
    try :
        print(f"{bcolors.FAIL} {variable}")
        if ( message != "" ):
            print(f"{bcolors.BOLD} {message}")

        print(bcolors.ENDC)
    except Exception as e :
        print( e )

def Debug( variable, message = "" ):
    try :
        print(f"{bcolors.OKCYAN} {variable}")
        if ( message != "" ):
            print(f"{bcolors.BOLD} {message}")

        print(bcolors.ENDC)
    except Exception as e:
        print( e )

def Inform( variable = "", message = ""):
    try :
        if variable != "":
            print(f"{bcolors.OKGREEN} {variable}")
        if message != "":
            print(f"{bcolors.BOLD} {message}")
        print(bcolors.ENDC)
    except Exception as e :
        print( e )

def Log( variable, code = 'd', message = "" ):
    if ( code == 'e' ):
        Error(variable, message)
    else :
        Debug(variable, message)



if __name__ == "__main__":
    y = "Fatal Sys Call... Removing BIOS..."
    x = 17

    Error( y, "(jk)" )
    Debug( x, "Seventeen")
