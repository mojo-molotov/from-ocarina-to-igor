---
title: "Chapter 03 — Functional programming with Ocarina"
description: "How and why Ocarina applies functional programming: a cross-cutting rereading of the framework's mechanics from the FP angle."
weight: 4
date: 2026-05-20
tags: ["functional"]
sidebar:
  open: true
---

# Chapter 03&nbsp;—&nbsp;Functional programming with Ocarina

> How Ocarina **applies** functional programming and **why**. This chapter is more _transversal_ than the others&nbsp;—&nbsp;it revisits the framework's mechanics from an FP angle.

## Outline

|  #  | File                                                                             | Topic                                                                                |
| :-: | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| 01  | [`01-effect-thunk-result.md`](01-effect-thunk-result.md)                         | `Effect`, `Thunk[T]`, `Result[T]`.                                                   |
| 02  | [`02-closures-ioc.md`](02-closures-ioc.md)                                       | Closures as the primitive of inversion of control.                                   |
| 03  | [`03-lazy-evaluation.md`](03-lazy-evaluation.md)                                 | Laziness everywhere: ChainRunner, validate.execute, Watcher callback, lazy prefixes. |
| 04  | [`04-fold-reduce.md`](04-fold-reduce.md)                                         | `reduce` (fold left) in `chain_actions`.                                             |
| 05  | [`05-declarative.md`](05-declarative.md)                                         | Declarative programming: a scenario _describes_, doesn't execute.                    |
| 06  | [`06-pep-695-generics.md`](06-pep-695-generics.md)                               | PEP 695 generics, `TypeVar bound`, `type X[T] = ...`.                                |
| 07  | [`07-discriminated-unions-typeguards.md`](07-discriminated-unions-typeguards.md) | Discriminated unions + `TypeGuard` + `@final` = "_sealed_" unions.                   |

## Why a dedicated chapter

Ocarina's code is small but **embodies** a serious number of FP patterns. This chapter names them, justifies them, and points to where they live in the code.

Holy Book quote (chapter "First feedbacks"):

> _Twisting Ocarina's ROP (Railway Oriented Programming) implementation until it lost all meaning, since they didn't even know what ROP is,_ …
> _Forcing their clueless take on lazy evaluation and IoC down my throat like it's gospel,_ …
> _"Explaining" imperative vs. declarative programming to me while spewing complete nonsense,_ …
