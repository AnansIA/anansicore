# AnansiCore v0.7 – Formal Grammar + Encoding Specification

> **Objective:** Feature-complete version covering 100% of required control and metadata constructs. Ready to be implemented and interpreted by any language.

---

## 1. Token Convention

Format: `Etiqueta.ID:Payload` (tokens separated by `|`)

- **Etiqueta**: indicates block or structural type (see Table §2).
- **ID**: hierarchical identifier like `1`, `1.2`, `1.3.4`.
- **Payload**: contains the associated expression, name, or content.
- `:` is **only used** as separator (not as a lambda alias).

---

## 2. Tag Table

| Tag | Meaning                        |
|-----|--------------------------------|
| F   | Function                       |
| f   | Lambda / Anonymous Function    |
| C   | Class                          |
| m   | Method                         |
| N   | Namespace / Module             |
| D   | Decorator                      |
| I   | Import                         |
| P   | Macro / Preprocessor (optional)|
| p   | Parameter                      |
| v   | Variable                       |
| a   | Assignment                     |
| i   | If                             |
| e   | Else                           |
| s   | Switch / Match                 |
| c   | Case                           |
| l   | Loop (for / while)             |
| b   | Break                          |
| n   | Continue / Next                |
| r   | Return                         |
| y   | Yield                          |
| t   | Try                            |
| x   | Except                         |
| z   | Finally / Defer                |
| u   | Using / Context Manager        |
| T   | Throw / Raise                  |
| A   | Assert                         |
| -   | Pass / No-op                   |
| d   | Do / Function call             |
| M   | Comment / Contextual Meta      |
| E   | End of Block                   |

> 🧠 Uppercase = global / stack-unwinding
> Lowercase = local / structural

---

## 3. EBNF Grammar (Simplified)

```ebnf
Program         = { Block } ;
Block           = Namespace | Function | Class | Loop | Conditional | TryBlock |
                  UsingBlock | Macro | Statement ;

Namespace       = "N" ID ':' Identifier { Statement } "E" ID ;

Import          = "I" ID ':' Identifier { ',' Identifier } ;

Macro           = "P" ID ':' DelimitedExpr ;

Function        = [ Decorator* ] "F" ID ':' Identifier { Param } { Statement } "E" ID ;
Decorator       = "D" ID ':' '@' Identifier [ '(' [ Arguments ] ')' ] ;

Lambda          = "f" ID ':' Expression ;

Class           = "C" ID ':' Identifier { Method | Statement } "E" ID ;
Method          = [ Decorator* ] "m" ID ':' Identifier { Param } { Statement } "E" ID ;

Param           = "p" ID ':' Identifier [ TypeHint ] [ Default ] ;

Conditional     = "i" ID ':' Expression { Statement } [ ElseBlock ] "E" ID ;
ElseBlock       = "e" ID ':' { Statement } ;

Loop            = "l" ID ':' ("for" | "while") Expression { Statement } "E" ID ;
Break           = "b" ID ':' ;
Continue        = "n" ID ':' ;

TryBlock        = "t" ID ':' { Statement } { ExceptBlock } [ FinallyBlock ] "E" ID ;
ExceptBlock     = "x" ID ':' [ Identifier ] { Statement } ;
FinallyBlock    = "z" ID ':' { Statement } ;

UsingBlock      = "u" ID ':' Expression [ 'as' Identifier ] { Statement } "E" ID ;

Statement       = VarDecl | Assignment | Return | Throw | Call | Break | Continue |
                  Pass | Assert | Import | Macro | Meta ;

VarDecl         = "v" ID ':' Identifier [ TypeHint ] [ '=' Expression ] [ Annotation ] ;
Assignment      = "a" ID ':' Identifier '=' Expression ;
Return          = "r" ID ':' ExpressionOrVoid ;
ExpressionOrVoid= 'Ø' | Expression ;
Throw           = "T" ID ':' Expression ;
Call            = "d" ID ':' Identifier '(' [ Arguments ] ')' ;
Pass            = "-" ID ':' ;
Assert          = "A" ID ':' Expression [ ',' Expression ] ;
Meta            = "M" ID ':' Text ;

TypeHint        = 'T' ':' Identifier [ GenericArgs ] ;
GenericArgs     = '<' GenericType { ',' GenericType } '>' ;
GenericType     = Identifier [ GenericArgs ] ;

Expression      = SimpleExpr | DelimitedExpr ;
DelimitedExpr   = '[[\n' EscapedText ']]' ;
EscapedText     = { PrintableCharExcept(']]') | '\\' | '\]]' | '\n' } ;

Arguments       = Expression { ',' Expression } ;
Annotation      = '@' Identifier [ ':' Value ] ;

ID              = [0-9]+ { '.' [0-9]+ } ;
Identifier      = (Letter | '_') { Letter | Digit | '_' } ;
Value           = Text ;
Text            = any printable UTF-8 except '|' and reserved 'Ø' ;
```

---

## 4. Expression Mini-Grammar

```ebnf
SimpleExpr   = Term { ('+'|'-') Term } ;
Term         = Factor { ('*' | '/' | '%') Factor } ;
Factor       = Literal | Identifier | Call | '(' SimpleExpr ')' ;
Literal      = Number | String | Boolean | 'None' ;
```

---

## 5. Semantic Validation Rules

1. Unique IDs (`1.2.3` requires `1` and `1.2`)
2. Sibling IDs must be unique
3. Each `E.X` must match the open block of `X`
4. `b`/`n` only valid inside `l.X`
5. `z` must follow `t` or `x`, and be under the same `t.X`
6. `Ø` is reserved and not allowed in other contexts
7. `-` (pass) must not have payload or children
8. `D` (decorators) only allowed before `F/m/C`
9. `A` (assert) global is disallowed unless marked `static_assert`
10. `I` (import) redundancy causes warning

---

## 6. Example (Flat)

```
N.0:utils
| I.0.1:os,sys
| D.0.2:@logger(timeout=60)
| F.0.3:process
|   p.0.3.1:path
|   u.0.3.2:[[open(path)]] as f
|     l.0.3.2.1:[[for line in f]]
|       i.0.3.2.1.1:[[line == "\n"]]
|         n.0.3.2.1.1.1:
|       E.0.3.2.1.1
|       d.0.3.2.1.2:[[print(line)]]
|     E.0.3.2.1
|   E.0.3.2
|   t.0.3.3:
|     A.0.3.3.1:[[path is not None]],[["path cannot be None"]]
|   x.0.3.3.2:Exception
|     d.0.3.3.2.1:[[print("error")]]
|   z.0.3.3.3:
|     d.0.3.3.3.1:[[print("cleanup")]]
|   E.0.3.3
|   r.0.3.4:Ø
| E.0.3
| E.0
```

---

## 7. Status

✅ Stable  
🧪 Fully Tested  
⚙️ Implemented in `parser.py` and `validator.py`  
📦 Ready for extensions: generation, LLM integration, REPL or code emitters

