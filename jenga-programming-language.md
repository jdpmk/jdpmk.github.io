---
title: 'Jenga: a stack-oriented, concatenative programming language'
author: Joydeep Mukherjee
date: May 26, 2023
abstract: 'In this article, I describe Jenga, a stack-oriented, concatenative programming language I wrote several months ago as an exercise to explore a new (somewhat esoteric) programming paradigm and apply my recently-acquired knowledge of programming languages from [CS 421](https://courses.grainger.illinois.edu/cs421/fa2022/) at UIUC. I implemented an interpreter for the language in OCaml, using standard tools including (ocaml)yacc and (ocaml)lex. References, source code, and example Jenga programs can be found in the [project repository on GitHub](https://github.com/jdpmk/jenga).'
---

## Stack-oriented and concatenative programming

[Stack-oriented programming languages](https://en.wikipedia.org/wiki/Stack-oriented_programming)
execute in the frame of a single stack which contains both data and commands.
Data items are pushed onto the top of the stack. Commands manipulate the items
of the stack (usually the items at the top).

One of the simplest examples of a stack-oriented language is a simple
[Reverse Polish notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation)
calculator.

```
"1 2 + 3 * 3 /" evaluates to "3"

        +           *       /
    2   2       3   3       3
1   1   1   3   3   3   9   9   3

================================>

    state of the stack during
           execution
```

In this example, the semantics of the language are relatively straightforward:
integer literals are data items pushed onto the stack, while operators like
`+`, `-`, `*`, and `/` are arithmetic operators which operate on the top two
items of the stack. Generally, these operators can be any
[n-ary](https://en.wikipedia.org/wiki/Arity) relation or function.

Even more broadly, this represents the style of
[concatenative programming](https://en.wikipedia.org/wiki/Concatenative_programming_language).
The sequential application of functions can elegantly express the notion
of function composition. For example, the following statement in C,

```c
foo(bar(baz(x)));
```

can be equivalently written in Jenga, as,

```c
x baz bar foo
```

## Language intrinsics

The core of the language is rather simple, supporting basic constructs such as:

- control flow (conditionals and loops)
- arithmetic, logical, and comparison operators
- minimal I/O (right now, it's really just O)
- a collection of stack manipulation operators
(inspired by [Forth](https://en.wikipedia.org/wiki/Forth_(programming_language)))
- static memory

A complete list can be found in the
[language specifications](https://github.com/jdpmk/jenga/blob/master/SPECIFICATIONS.md)
on GitHub.

## Language semantics

Now, we'll discuss language semantics, motivated by snippets of Jenga code:

Data can be pushed onto the stack as a literal:

```c
1  # now the integer "1" is on the stack
```

The programmer should ensure that the stack is empty at the termination of
the program. Otherwise, type-checking fails.

Functions and operators can be applied on data:

```c
1 2 + println  # prints "3"
```

Note that in the above example, `println` "consumes" the value on the stack, 3,
so at the termination of the program, the stack is empty.

Programs which apply functions or operators to less data than expected will
fail during type-checking:

```c
println  # type-checking fails, expected a value but found none
```

Conditionals work by executing the condition of the statement, checking the top
of the stack for a boolean value, and taking the corresponding branch:

```c
# prints "odd"

if 2023 2 % 0 = then
    "even" println
else
    "odd" println
end
```

While loops work similarly:

```c
# prints "0 1 2 3 4" (newline separated)

0 while dup 5 != do
    dup println
    1 +
end drop
```

There are more nuances to the semantics which are enforced during type-checking
(see below). For example, loops and conditionals should neither create nor
delete data from the stack. Intrinsic operators expect arguments of given types
(for example, adding two strings is not well-defined in Jenga; integers are
expected).

## Memory model

Static memory was introduced as a way to write more useful programs that can
do significant computation. Without this, the working memory of a Jenga program
is just the stack which the program is operating on!

Static memory is allocated as an integer, string, or array with fixed size.
Each piece of memory is given an identifier which can be read from or written
to. I find the syntax of "piping" the value read from a static memory
identifier into a function (such as `println`) rather elegant.

```c
alloc x as int 0 end

# ...some computation on x...

# place the value of `x` onto the stack, then print it,
# or equivalently, pass the value of `x` to `println`

x -> println
```

## Type-checking

The type system for Jenga is rather simple. The language is statically-typed
so the expected type at each step of execution can be inferred from the data
and functions placed on the stack. Note that there are no type annotations,
apart from those placed in static memory declarations: types for literal
integers and strings are inferred.

To type-check Jenga, we simply execute the program but maintain a "type stack"
rather than a "value stack". For example, for the following program,

```c
1 2 + println
```

our type stack looks like:

```
      +
int   int
int   int   int   ___

====================>

 state of the stack
during type-checking
```

Conditional statements and loops are type-checked by recursively type-checking
the body of the construct. Recursively applying this approach allows us to
type-check nested conditional statements and loops. Note that loops are
type-checked statically in a single pass, therefore type-checking is
guaranteed to terminate, even if the program does not terminate when executed.

For a more complicated example, let's consider the following program, which
computes the sequence described by the
[Collatz conjecture](https://en.wikipedia.org/wiki/Collatz_conjecture).

```c
# An example which *tries to* implement the recurrence described
# by the Collatz conjecture
#
# Expected output:
# 42
# 21
# 64
# 32
# 16
# 8
# 4
# 2
# 1

42
while dup 1 != do
    dup println
        if dup 2 % 0 = then
            2 /
        else
            3 * + 1
        end
    end
println
```

The type-checker fails, producing the following error message.

```txt
Fatal error: exception Jenga.Exceptions.TypeError("cannot
execute `+`. expected two items of type `int` on the stack
but found one item or none")
```

It seems like `+` is executing without enough integers on the stack. Upon
inspecting our call to `+`, we seem to have placed it out of order: the `+`
should be placed after 1 on the stack, since `3 * x + 1` is equivalent to
`3 x * 1 +` in postfix notation. Making this change fixes the error and the
program runs as expected (see the corrected program at
[collatz.jg](https://github.com/jdpmk/jenga/blob/master/examples/collatz.jg)).

This is a great example of how an effective type-checker greatly enhances the
development experience and helps catch major issues before they occur at
runtime.

Jenga's type-checker can identify mismatched arguments (in both the number of
arguments and type of arguments), unexpected types being introduced (for
example, in the body of a conditional or loop), and unhandled data on the stack
at the end of the program.

## Evaluation

As suggested above, evaluation of a Jenga program occurs in a similar manner
to type-checking but with a "value stack" instead. For example, for the
following program,

```c
1 2 + println
```

our value stack looks like:

```
    +
2   2
1   1   3   ___

====================>

 state of the stack
 during execution
```

For brevity, the formal semantics of type-checking and evaluation for all
constructs in the language have been omitted but the implementation can be
found in
[types.ml](https://github.com/jdpmk/jenga/blob/master/lib/types.ml) and
[evaluate.ml](https://github.com/jdpmk/jenga/blob/master/lib/evaluate.ml),
respectively.

## Turing-completeness and computability

We can say that a system which can simulates a Turing machine is Turing
complete. Therefore, if our language can simulate a Turing complete cellular
automaton, like
[Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life),
then it is also Turing complete!

Here is an example implementation of
[Rule 110](https://en.wikipedia.org/wiki/Rule_110), a simpler Turing complete
cellular automaton (original source code also found in the examples directory
of the project repository, in
[rule110.jg](https://github.com/jdpmk/jenga/blob/master/examples/rule110.jg)).

```c
# An implementation of the Rule 110 cellular automaton
#
# See:
# - https://en.wikipedia.org/wiki/Rule_110
# - https://mathworld.wolfram.com/Rule110.html

alloc ON  as string "X" end
alloc OFF as string "O" end

alloc n     as int        61  end
alloc state as string[61] "O" end
alloc next  as string[61] "O" end
alloc slice as string[3]  "O" end

alloc iterations as int 40 end

# Set the middle element to ON
state n -> 2 / ON -> <-

# Run the automaton for the given number of iterations
0 while dup iterations -> != do
    # Print the current state
    0 while dup n -> != do
        state over -> print
        1 +
    end drop
    "" println

    # Populate the next state
    0 while dup n -> != do
        # Indices to read from the current state
        dup 1 -
        dup 1 +
        dup 1 +

        # Store a slice of three cells based on the current index
        # with bounds checking (0 <= i < n)

        # slice[i - 1]...
        rot if dup -1 = then slice 0 OFF -> <-
        else dup slice 0 rot state swap -> <- end

        # slice[i]...
        rot dup slice 1 rot state swap -> <-

        # slice[i + 1]...
        rot if dup n -> = then slice 2 OFF -> <-
        else dup slice 2 rot state swap -> <- end

        drop drop drop

        # Match pattern to determine next state
        if slice 0 -> ON -> =
           slice 1 -> ON -> =
           slice 2 -> ON -> =
           && &&
        then
            next over OFF -> <-
        else end

        if slice 0 -> ON  -> =
           slice 1 -> ON  -> =
           slice 2 -> OFF -> =
           && &&
        then
            next over ON -> <-
        else end

        if slice 0 -> ON  -> =
           slice 1 -> OFF -> =
           slice 2 -> ON  -> =
           && &&
        then
            next over ON -> <-
        else end

        if slice 0 -> ON  -> =
           slice 1 -> OFF -> =
           slice 2 -> OFF -> =
           && &&
        then
            next over OFF -> <-
        else end

        if slice 0 -> OFF -> =
           slice 1 -> ON  -> =
           slice 2 -> ON  -> =
           && &&
        then
            next over ON -> <-
        else end

        if slice 0 -> OFF -> =
           slice 1 -> ON  -> =
           slice 2 -> OFF -> =
           && &&
        then
            next over ON -> <-
        else end

        if slice 0 -> OFF -> =
           slice 1 -> OFF -> =
           slice 2 -> ON  -> =
           && &&
        then
            next over ON -> <-
        else end

        if slice 0 -> OFF -> =
           slice 1 -> OFF -> =
           slice 2 -> OFF -> =
           && &&
        then
            next over OFF -> <-
        else end

        1 +
    end drop

    # Copy the next state to the current state
    0 while dup n -> != do
        state over next over -> <-
        1 +
    end drop
    
    1 +
end drop
```

This is far from a rigorous evaluation of the Turing-completeness of the
language but it suffices for this article.

## Future directions

The stack-oriented programming paradigm is rather simple to understand, making
it somewhat straightforward to design and write a minimally viable programming
language. It's also a great exercise to explore new ways of thinking about code.
Seriously, even writing something as "simple" as
[fibonacci.jg](https://github.com/jdpmk/jenga/blob/master/examples/fibonacci.jg)
can be really tricky when juggling data around the stack!

I would highly recommend attempting to write a language like this, especially
if you are new to programming language implementation (like I am) and only
know some of the basics.

To close, here are a couple of enhancements for Jenga I had in mind, with the
goal of improving its practicality and expressiveness.

### Macros

A striking omission from the language is the function or procedure abstraction
(ignoring intrinsics like `println`). However, I believe a simpler abstraction
that can be just as powerful in this language are macros. Think simple,
[C-style](https://en.wikipedia.org/wiki/C_preprocessor) string replacement.

A simple motivation for this sort of a feature can actually be found in the
Rule 110 implementation above!

In order to express conditions, in C, of the form,

```c
a && b && c
```

we write, in Jenga,

```c
a b c && &&
```

The postfix nature of the syntax can make this expression difficult for humans
to parse, especially when `a`, `b`, and `c` themselves are also more
complicated expressions.

What if we could instead define the following macro?

```c
macro &&& do
    && &&
end
```

Then, we could write,

```c
a b c &&&
```

which, before type-checking and evaluation, would expand to,

```c
a b c && &&
```

which is an equivalent program!

Furthermore, to avoid macro expansions, we could even enhance the type-checker
to determine a signature for a given macro. For example, the above macro `&&&`
could have the type signature,

```c
&&& : (bool, bool) -> bool
```

meaning it takes two booleans off the stack and produces a boolean.

The example above is more like
[syntactic sugar](https://en.wikipedia.org/wiki/Syntactic_sugar)
(i.e. it could be quickly implemented by introducing a new symbol to the
core language) so let's give another example: the absolute value "function"
(it's still just a macro).

```c
macro abs do
    if dup 0 < then
        -1 *
    else
        # non-negative, do nothing
    end
end
```

which could have the type signature,

```c
abs : int -> int
```

meaning it takes one integer off the stack and produces another integer.

Let's go one step further.

```c
# this macro has the signature
# negate : int -> int
macro negate do
    -1 *
end

macro abs do
    if dup 0 < then negate else end
end
```

We can go even further by creating a predicate called `negative`.

```c
# this macro has the signature
# negative : int -> bool
macro negative do
    0 <
end

# this macro has the signature
# negate : int -> int
macro negate do
    -1 *
end

macro abs do
    if dup negative then negate else end
end
```

Combining macros with concatenative style makes the code *really* expressive!

### Compilation

Another enhancement to the practicality of Jenga would be the ability to
compile a program to a native executable. As always, when moving from
interpretation to native execution, there is a potential for performance
improvements. I have not yet benchmarked the OCaml implementation but it feels
snappy.

### System calls

The ability to interact with system calls would greatly expand the
opportunity to write programs which do more "useful" I/O with arbitrary file
and network descriptors. It would be awesome to reimplement common utilities
like `cat` or `ls`, or even write a simple TCP server in Jenga.
