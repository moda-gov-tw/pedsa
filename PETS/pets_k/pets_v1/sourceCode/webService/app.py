import config
from app import app

import sys

#app.run(debug=True, host='0.0.0.0')
#app.run(debug=True)

global jarFileName


if __name__ == '__main__':
    #global jarFileName
    jarFileName = sys.argv[1]
    
    print jarFileName
    app.run(host='0.0.0.0',port=int("5088"),debug=True)
