import os, discord, ast, math, operator
from serpapi import GoogleSearch

try:
    TOKENFILE = open('.token','r+')
    TOKENS = TOKENFILE.readlines()
    DISCORDTOKEN = TOKENS[0]
    IMAGETOKEN = TOKENS[1]
except OSError:
    print('Error abriendo archivo')
    DISCORDTOKEN = os.environ['TOKEN']
    IMAGETOKEN = os.environ['IMAGES']

client = discord.Client()

@client.event
async def on_ready():
    print('Logeado {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('jrcal '):
    respuesta = handle(message.content.replace('jrcal ',''),message.author.name)
    await message.channel.send(respuesta)


def handle(args,user):
  if args == 'help' or args == '':
    return 'Escriba una operacion aritmetica'
  
  if args == 'git':
    return 'https://github.com/jg2kpy/jrbot'
  
  if args.startswith('-i'):
    querry = args.replace('-i ','')
    return querry_google_images(querry)
  
  if args.startswith('-e'):
    return 'Not implemented yer'


  try:
    evaluation = safe_eval(args)
    retorno = args + ' = ' + str(evaluation)
    print(user + ': '+ retorno)
    return retorno
  except Exception as ex:
    print(user + ': '+ args + ': Error')
    print(ex)
    return args + ': Error'
    

def querry_google_images(querry):
  params = {
    "q": querry,
    "tbm": "isch",
    "ijn": "0",
    "api_key": IMAGETOKEN
  }
  search = GoogleSearch(params)
  results = search.get_dict()
  images_results = results['images_results']
  return images_results[0]['original']

#Funcion prestada de Stack Overflow
def safe_eval(s):

    def checkmath(x, *args):
        if x not in [x for x in dir(math) if not "__" in x]:
            raise SyntaxError(f"Unknown func {x}()")
        fun = getattr(math, x)
        return fun(*args)

    binOps = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.Call: checkmath,
        ast.BinOp: ast.BinOp,
    }

    unOps = {
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.UnaryOp: ast.UnaryOp,
    }

    ops = tuple(binOps) + tuple(unOps)

    tree = ast.parse(s, mode='eval')

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.value
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            if isinstance(node.left, ops):
                left = _eval(node.left)
            else:
                left = node.left.value
            if isinstance(node.right, ops):
                right = _eval(node.right)
            else:
                right = node.right.value
            return binOps[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.operand, ops):
                operand = _eval(node.operand)
            else:
                operand = node.operand.value
            return unOps[type(node.op)](operand)
        elif isinstance(node, ast.Call):
            args = [_eval(x) for x in node.args]
            r = checkmath(node.func.id, *args)
            return r
        else:
            raise SyntaxError(f"Bad syntax, {type(node)}")

    return _eval(tree)


def solve_funtion(funtion, x, y):
    funtion2 = funtion.replace('x',str(x))
    funtion2 = funtion2.replace('y',str(y))
    return safe_eval(funtion2)


def euler(funtion,x0,y0,x,h):
    N = abs(((x - x0)/h)) + 1
    xn = x0
    yn = y0
    yn2 = yn
    for i in range(1,int(N)):
        xn = xn + h
        yn2 = yn + h*solve_funtion(funtion,xn,yn)
        yn = yn + (h/2)*(solve_funtion(funtion,xn,yn)+solve_funtion(funtion,xn,yn2))

    return yn

client.run(DISCORDTOKEN)