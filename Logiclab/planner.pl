% planner.pl  -  Tasks 6, 7 and 8 of the laboratory
% Run with:  swipl planner.pl     then type queries, e.g.  ?- can_move(a,b).

% ---- Task 6: warehouse facts and a rule ------------------------------------
connected(a,b).
connected(b,a).
connected(b,c).
connected(c,b).

can_move(X,Y) :-
    connected(X,Y).

% ---- Task 7: checking proposed moves --------------------------------------
valid_move(X,Y) :-
    connected(X,Y).

% Check a whole sequence of moves, e.g. ?- valid_move_sequence([a,b,c]).
valid_move_sequence([_]).
valid_move_sequence([X,Y|Rest]) :-
    valid_move(X,Y),
    valid_move_sequence([Y|Rest]).

% ---- Task 8: wet road ------------------------------------------------------
wet_road.
slippery :-
    wet_road.
reduce_speed :-
    slippery.
