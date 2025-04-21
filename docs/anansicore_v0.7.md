# AnansiCore v0.7 – Gramática Formal + Especificación de Codificación

> Objetivo: Versión “feature‑complete” que cubre el 100 % de los constructos de control y metadatos requeridos, lista para ser implementada en el parser de RepoMe.

---

## 1. Convención de tokens

`Etiqueta.ID:Payload`   (tokens separados por `|`)

- Etiqueta = identificador de tipo de nodo (tabla §2).
- ID = jerarquía «n.n.n». Los hermanos no pueden repetir sufijo.
- Payload = nombre, expresión, tipo, etc.
- El caracter `:` se usa solo como separador; nunca como alias.

---

## 2. Tabla completa de etiquetas

| Etiqueta | Significado                         |
| -------- | ----------------------------------- |
| F        | Función                             |
| f        | Lambda / función anónima            |
| C        | Clase                               |
| m        | Método                              |
| N        | Namespace / módulo                  |
| D        | Decorador global                    |
| I        | Import                              |
| P        | Macro / Pre‑procesador (*opcional*) |
| p        | Parámetro                           |
| v        | Variable                            |
| a        | Asignación                          |
| i        | If                                  |
| e        | Else                                |
| s        | Switch / Match                      |
| c        | Case                                |
| l        | Loop (for / while)                  |
| b        | Break                               |
| n        | Continue / Next                     |
| r        | Return                              |
| y        | Yield                               |
| t        | Try                                 |
| x        | Except                              |
| z        | Finally / Defer                     |
| u        | Using / Context manager             |
| T        | Throw / Raise                       |
| A        | Assert                              |
| -        | Pass / No‑op                        |
| d        | Do / Llamado a función              |
| M        | Comentario / metadato contextual    |
| E        | Fin de bloque                       |

Las mayúsculas indican elementos con efecto de ámbito global o unwind de pila; minúsculas para flujo local o estructura.

---

## 3. Reglas EBNF actualizadas

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
EscapedText     = { PrintableCharExcept(']]') | '\' | '\]]' | '\n' } ;

Arguments       = Expression { ',' Expression } ;
Annotation      = '@' Identifier [ ':' Value ] ;

ID              = [0-9]+ { '.' [0-9]+ } ;
Identifier      = (Letter | '_' ) { Letter | Digit | '_' } ;
Value           = Text ;
Text            = any printable UTF‑8 except '|' and reserved token 'Ø' ;

---

### Anexo A – mini‑gramática `SimpleExpr`

SimpleExpr   = Term { ('+'|'-') Term } ;
Term         = Factor { ('*' | '/' | '%') Factor } ;
Factor       = Literal | Identifier | Call | '(' SimpleExpr ')' ;
Literal      = Number | String | Boolean | 'None' ;

---

## 4. Validaciones semánticas obligatorias

1. Jerarquía de IDs – un token `1.2.3` sólo es válido si existen `1` y `1.2`.
2. Unicidad de hermanos – dentro de un mismo padre, los sufijos deben ser únicos.
3. Cierre de bloques – cada `E.X` debe cerrar el bloque abierto con el mismo prefijo.
4. `b` / `n` contextuales – sólo dentro de `l.X` del mismo ancestro.
5. `z` – debe seguir al último `x` o directamente al `t` correspondiente.
6. `Ø` – reservado: no puede aparecer en `Text` ni `Identifier`.
7. `-` – pass: sin payload ni hijos.
8. Decorador – sólo puede preceder inmediatamente a `F`, `m` o `C`.
9. Assert – prohibido al nivel de `Program` salvo flag `static_assert` habilitado.
10. Import – redundancias múltiple‑import mismo nombre producen warning.

---

## 5. Ejemplo completo v0.7

N.0:utils
| I.0.1:os,sys
| P.0.2:[[#define MAX 10]]
| D.0.3:@logger(timeout=60)
| F.0.4:procesar
|   p.0.4.1:path
|   u.0.4.2:[[open(path)]] as f
|     l.0.4.2.1:[[for linea in f]]
|       i.0.4.2.1.1:[[linea == "\n"]]
|         n.0.4.2.1.1.1:
|       E.0.4.2.1.1
|       s.0.4.2.1.2:[[len(linea)]]
|         c.0.4.2.1.2.1:[[0]] :
|           b.0.4.2.1.2.1.1:
|         c.0.4.2.1.2.2:[[1]] :
|           -.0.4.2.1.2.2.1:
|       E.0.4.2.1.2
|       d.0.4.2.1.3:[[print(linea)]]
|     E.0.4.2.1
|   E.0.4.2
|   t.0.4.3:
|     A.0.4.3.1:[[path is not None]],[["path no puede ser None"]]
|   x.0.4.3.2:Exception
|     d.0.4.3.2.1:[[print("error")]]
|   z.0.4.3.3:
|     d.0.4.3.3.1:[[print("fin")]]
|   E.0.4.3
|   r.0.4.4:Ø
| E.0.4
| -.0.5:
| E.0

---

## 6. Cambios clave desde v0.6

| Cambio                      | Motivo                                         |
| ---------------------------| ---------------------------------------------- |
| Decorador con argumentos    | Soporta `@decorator(args)`                     |
| Import múltiple             | Un solo token `I` lista varios módulos         |
| Macro (`P`)                 | Permite directivas de pre‑procesador           |
| Mini‑gramática `SimpleExpr` | Resuelve la referencia pendiente               |
| Multilínea en `[[ ]]`       | `\n` dentro de `EscapedText`                 |
| Validaciones extra          | Unicidad de IDs, posición de decoradores, etc. |
| Ejemplo ampliado            | Incluye `continue`, `switch/case`, macro y más |
