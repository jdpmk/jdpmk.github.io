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
h = f . g
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
