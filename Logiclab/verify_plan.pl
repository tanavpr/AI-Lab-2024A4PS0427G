% verify_plan.pl  -  an independent STRIPS-style plan verifier in Prolog
%
% The Python program GENERATES a plan; this file CHECKS it using only the
% logical description of the warehouse (facts + rules).
%
% State  : an ordered set (sorted list) of facts, e.g. [at(package,a), at(robot,a)]
% Action : action(Term, PosPre, NegPre, Add, Delete)
%
% Usage (from a shell):
%   swipl -q -g "verify([pickup(package,a),move(a,b),move(b,c),drop(package,c)]),halt" verify_plan.pl

:- use_module(library(ordsets)).

connected(a,b).
connected(b,a).
connected(b,c).
connected(c,b).

location(a). location(b). location(c).

initial([at(package,a), at(robot,a)]).
goal([at(package,c)]).

% action(Name, PositivePreconditions, NegativePreconditions, AddList, DeleteList)
action(move(X,Y),
       [at(robot,X)], [],
       [at(robot,Y)], [at(robot,X)]) :-
    connected(X,Y).
action(pickup(package,L),
       [at(robot,L), at(package,L)], [],
       [holding(package)], [at(package,L)]) :-
    location(L).
action(drop(package,L),
       [at(robot,L), holding(package)], [],
       [at(package,L)], [holding(package)]) :-
    location(L).

% S |= Preconditions(A)
applicable(State, A) :-
    action(A, Pos, Neg, _, _),
    list_to_ord_set(Pos, PosSet),
    ord_subset(PosSet, State),
    list_to_ord_set(Neg, NegSet),
    ord_intersection(NegSet, State, []).

% S' = (S - Delete) + Add
apply(State, A, NewState) :-
    action(A, _, _, Add, Del),
    list_to_ord_set(Add, AddSet),
    list_to_ord_set(Del, DelSet),
    ord_subtract(State, DelSet, S1),
    ord_union(S1, AddSet, NewState).

% valid_plan(+State, +Plan, +Goal): every action applicable in turn, goal holds at end
valid_plan(State, [], Goal) :-
    list_to_ord_set(Goal, GoalSet),
    ord_subset(GoalSet, State).
valid_plan(State, [A|Rest], Goal) :-
    applicable(State, A),
    apply(State, A, Next),
    valid_plan(Next, Rest, Goal).

% Same check, printing a trace and the reason for any failure
trace_plan(State, [], Goal) :-
    format("final state: ~w~n", [State]),
    list_to_ord_set(Goal, GoalSet),
    (   ord_subset(GoalSet, State)
    ->  writeln('goal satisfied')
    ;   writeln('goal NOT satisfied'), fail ).
trace_plan(State, [A|Rest], Goal) :-
    (   applicable(State, A)
    ->  apply(State, A, Next),
        format("~w  applicable -> ~w~n", [A, Next]),
        trace_plan(Next, Rest, Goal)
    ;   format("~w  NOT applicable in ~w~n", [A, State]),
        fail ).

verify(Plan) :-
    initial(S0), goal(G),
    list_to_ord_set(S0, S),
    (   trace_plan(S, Plan, G)
    ->  writeln('PLAN VALID')
    ;   writeln('PLAN INVALID') ).
