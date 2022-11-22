from enum import Enum, auto
from numbers import Number
from dataclasses import dataclass
from typing import Any, Optional




class TokenKind(Enum):
    MUL = auto()
    ADD = auto()
    SUB = auto()
    NUM = auto()

    FUNC_DEF = auto()
    FUNC_BODY = auto()

    INIT_SCOPE = auto()
    END_SCOPE = auto()


    """
    IDENTIFIER = auto()
    CONST_DECL = auto()
    VAR_DECL = auto()
    """

@dataclass
class Token:
    kind: TokenKind
    pos: Optional[tuple[int, int]] = None
    #precedence: int
    value: Optional[Any] = None

    def __eq__(self, other):
        return self.kind == other.kind



def tokenize(program_str):
    tokens = list()
    assert len(TokenKind) == 8, "Non exaustive pattern in `tokenize` function"

    index = 0
    line = 0
    while index < len(program_str):
        char = program_str[index]
        pos = (line, index)
        match char:
            case '\n': line += 1
            case '+' : tokens.append(Token(TokenKind.ADD, pos))
            case '-' : tokens.append(Token(TokenKind.SUB, pos))
            case '*' : tokens.append(Token(TokenKind.MUL, pos))

            case 'λ' : tokens.append(Token(TokenKind.FUNC_DEF, pos))
            case '.' : tokens.append(Token(TokenKind.FUNC_BODY, pos))

            case '(' : tokens.append(Token(TokenKind.INIT_SCOPE, pos))
            case ')' : tokens.append(Token(TokenKind.END_SCOPE, pos))

            case v if v.isdigit():
                number = list()
                decimal = False
                while index < len(program_str):
                    c = program_str[index]
                    if not (c.isdigit() or (c == '.' and not decimal)):
                        index-=1
                        break

                    if c == '.' and not decimal:
                        decimal = True

                    number.append(c)
                    index+=1

                # TODO: lembrar que 1. 2 viram 2 tokens, 1.0 e 2, isso é passível de erro
                tokens.append(Token( TokenKind.NUM, pos, value=(float if decimal else int)(''.join(number))))

        index+=1

    return tokens



"""
fun := <func_def> <arg_list> <func_body> <body>
func_def := λ
arg_list := <identifier> <arg_list> | <identifier> | NULL
func_body := .

TODO: adicionar declaração de variaveis e constantes
body := <expr>

expr := <fun> <expr>
      | <expr> * <expr>
      | <expr> / <expr>
      | <expr> + <expr>
      | <expr> - <expr>
      | - <expr> // ???
      | ( <expr> )
      | <num>
"""


def parse(tokens: list[Token]):
    #assert len(TokenKind) == 8, "Non exaustive pattern in `parse` function"


    if len(tokens) == 1 and tokens[0].kind == TokenKind.NUM:
        return Expr(ExprKind.NUM, single = tokens[0].value)


    priority = [
            (TokenKind.MUL , lambda l, r : Expr(ExprKind.MUL, l, r)),
            (TokenKind.SUB , lambda l, r : Expr(ExprKind.SUB, l, r)),
            (TokenKind.ADD , lambda l, r : Expr(ExprKind.ADD, l, r))]

    for operator, constructor in priority[::-1]:
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token.kind == TokenKind.INIT_SCOPE:
                found = 0
                idx = 1
                while idx < len(tokens[index:]):
                    t = tokens[idx]
                    if t.kind == TokenKind.INIT_SCOPE:
                        found -= 1
                    elif t.kind == TokenKind.END_SCOPE:
                        found += 1

                    if found == 1:
                        break

                    idx += 1

                index += idx


            if token.kind == operator:

                left_tokens = tokens[:index]
                right_tokens = tokens[index+1:]

                if not left_tokens or not right_tokens:
                    assert False, "error not implemented"
                    # TODO: expressão estilo `1 + `, onde não existe uma parte
                    pass

                left = parse(left_tokens)
                right = parse(right_tokens)

                return constructor(left, right)

            index += 1

    if tokens[0].kind == TokenKind.INIT_SCOPE and tokens[-1].kind == TokenKind.END_SCOPE:
        return parse(tokens[1:-1])


class ExprKind(Enum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    NUM = auto()
    SCOPED = auto()

@dataclass
class Expr:
    kind  : ExprKind
    left  : Optional[Any] = None
    right : Optional[Any] = None
    single: Optional[Any] = None


def eval_expr(expr):
    match expr:
        case Expr(ExprKind.NUM, single=v)   : return v
        case Expr(ExprKind.ADD, left, right): return eval_expr(left) + eval_expr(right)
        case Expr(ExprKind.SUB, left, right): return eval_expr(left) - eval_expr(right)
        case Expr(ExprKind.MUL, left, right): return eval_expr(left) * eval_expr(right)

"""
TODO:
- constant and function declaration `<identifier> : <body>`
- variable? declaration `<identifier> = <body>`?
"""

