---
title: 'Notes on "Category Theory for Programmers"'
author: Joydeep Mukherjee
date: October 15, 2023
abstract: My notes on ["Category Theory for Programmers" by Bartosz Milewski](https://github.com/hmemcpy/milewski-ctfp-pdf). I summarize key points and highlight interesting quotes and ideas mentioned in each chapter.
---

## Chapter 1

### Category: The Essence of Composition

We can think of categories as a collection of objects and arrows, or morphisms,
between these objects.

Morphisms compose. If $f : A \to B$ and $g : B \to C$ then there must be a
morphism $h : A \to C$.

1. Composition of morphisms is associative.

    - $f \circ g \circ h = (f \circ g) \circ h = f \circ (g \circ h)$

2. An identity or unit arrow on an object is a unit of composition.

    - If $f : A \to B$ then $f \circ \text{id}_A = f$ and $\text{id}_B \circ f = f$.

In Haskell,

```haskell
-- Identity function.
id :: a -> a
id x = x

-- Composition, given f :: a -> b and g :: b -> c.
h :: a -> c
h x = g f x

-- Or, in point-free notation.
h :: a -> c
h = g . f
```

In C++,

```cpp
// Identity function.
template <class T>
T id(T x) {
    return x;
}

// Composition, given `B f(A)` and `C g(B)`.
C h(A x) {
    return g(f(x));
}
```

> We need structure not because well-structured programs are pleasant to look
at, but because otherwise our brains can’t process them efficiently. We often
describe some piece of code as elegant or beautiful, but what we really mean is
that it’s easy to process by our limited human minds.

> The moment you have to dig into the implementation of the object in order to
understand how to compose it with other objects, you’ve lost the advantages of
your programming paradigm.

## Chapter 2

### Types and Functions

Types are finite or infinite sets of values. In Haskell, types like `String`
and `Integer` are infinite sets, while `Char` and `Int` (machine-type integer)
are finite.

The category $\textbf{Set}$ consists of objects which are sets and morphisms
which are functions. Unfortunately, types in Haskell do not correspond directly
to this notion of sets, due to the possibility of non-terminating computations
(see the [halting problem](https://en.wikipedia.org/wiki/Halting_problem)).

The category of Haskell types and functions is known as $\textbf{Hask}$. Each
type is extended by a special value, $\bot$ ("bottom"), which denotes a
non-terminating computation.

In Haskell, $\bot$ is denoted by `undefined`:

```haskell
f :: a -> b
f x = undefined

-- Since `undefined` is also a member of the type `a -> b`
f :: a -> b
f = undefined
```

Some tools for reasoning about programs include operational semantics and
denotational semantics.

Operational semantics describes the execution of a program in an "idealized
interpreter". To prove a useful property of the program, you need to execute
it.

On the other hand, denotational semantics assigns a mathematical interpretation
to each construct in the language. We can assert useful properties of programs
by proving properties of its components.

There is also a notion of pure functions. Pure functions produce the same value
given the same output, no matter how many times evaluated. They also must not
produce any side effects, unlike "dirty" functions.

Mathematical functions are pure. Haskell is a pure functional programming
language, so all functions in Haskell are also pure. We use monads to model
side effects (covered later). Basically all useful programs perform some sort
a side effect, so this is crucial.

Now going back to types. Types are just sets. So you may have a type with no
elements. This is Haskell's `Void` type (not the same as C++ `void`!).

```haskell
-- Cannot be called, no values in type `Void`.
absurd :: Void -> a
```

A type with one element is C++'s `void` type. In Haskell, the type (and its
corresponding singleton value) is `()` (pronounced "unit").

```haskell
f44 :: () -> Integer
f44 () = 44

-- Looks a lot like the equivalent call in C++! `f44();`
f44 ()
```

We can also map every value in a given type to the value of the singleton type,
`()`. In Haskell, this function is called `unit`, and is parametrically
polymorphic - it doesn't dependent on the type passed in (and in this case
doesn't depend on the value passed in either).

```haskell
unit :: a -> ()
unit _ -> ()
```

Types of two element sets are booleans. In Haskell, this is `Bool`, and is
defined as follows. Functions to `Bool` are known as predicates.

```haskell
data Bool = True | False

-- isAlpha is a predicate.
-- isAlpha :: Char -> Bool
-- This expression evaluates to `True`.
-- 'a' is an alphabetical character.
import Data.Char
isAlpha 'a'
```

> In a weakly typed language, the fact that a function now expects different
data cannot be propagated to call sites. Unit testing may catch some of the
mismatches, but testing is almost always a probabilistic rather than a
deterministic process. Testing is a poor substitute for proof.

## Chapter 3

### Categories Great and Small

A simple example is a trivial category with zero objects and zero morphisms.
This is sort of like an empty set.

Categories can be built from directed graphs. Nodes can be treated as objects.
We need an identity arrow at each node, and an arrow where the end of an arrow
coincides at an object from which another arrow begins. A category built from a
graph like this is called a free category, an example of free construction.

There are categories where the morphisms express a relation between objects.
For example, ordering. The "less than or equal" relation is a category,
satisfying:

- the identity morphism, e.g. $a \leq a$
- composition, e.g. $a \leq b, b \leq c \implies a \leq c$
- associativity

If we impose $a \leq b, b \leq a \implies a = b$, this is called a
partial order. If we further impose a relation between any two objects, we get
a total order.

A preorder is a thin category, where there is at most one morphism from $a$ to
$b$. $C(a, b)$ (or $\textbf{Hom}_{C}(a, b)$) is a hom-set, or the set of
morphisms from $a$ to $b$. In a preorder this is either an empty or singleton
set. Cycles may occur in a preorder but not in a partial order.

A monoid is a set with a binary operation, which is associative and has a
special unit element. An example is the natural numbers with zero over
addition. In Haskell, a type class exists for it:

```haskell
class Monoid m where
    mempty :: m
    mappend :: m -> m -> m
```

A monoid is a single object category with a set of morphisms following rules
for composition. We can always extract this set of morphisms from the single
object category: the hom-set $\textbf{M}(m, m)$ for single object $m$ in
category $\textbf{M}$. A binary operator in this set could be the composition
of morphisms.

Every categorical monoid (one-object category) defines a unique
set-with-binary-operator monoid.
