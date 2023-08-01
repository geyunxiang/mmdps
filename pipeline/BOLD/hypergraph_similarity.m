clear all;
n = 8;
E = {[3,4],[1,2,4,5,7,8],[2,5,6,8]};
A = hypergraph_to_incidencegraph(n,E);
% A = hypergraph_to_extended2section(n,E);

n = 8;
% E = {[4,5],[1,2,6,7,10,11],[3,8,9,12],[5,6,7,8]};
% E = {[1,2,4,5,7,8],[3,4],[2,5,6,8]};
E = {[3,4],[1,2,4,5,7,8],[2,5,6,8]};
B = hypergraph_to_incidencegraph(n,E);
% B = hypergraph_to_extended2section(n,E);

% Z = similarity_matrix(A,B,10e-9);
% A = [0,1,0;1,0,1;0,0,1];
% B = [0,1,0;1,0,1;0,0,1];
Z = similarity_matrix(A,B,10e-5);
function [A] = hypergraph_to_incidencegraph(n,E)
    m = numel(E);
    A = zeros(n+m,n+m);
    for idx = 1:numel(E)
        edge = cell2mat(E(idx));
            for idx_2 = 1:numel(edge)
                A(edge(idx_2), n + idx) = 1;
                A(n + idx,edge(idx_2)) = 1;
            end
    end
end


function [Z] = similarity_matrix(A,B, TOL)
    Z_0 = ones(size(B,1),size(A,1));
    mu(1:size(B,1),1:size(A,1)) = TOL;
    Z = Z_0;
    Z_previouseven = Z_0;
    k=1;
    while true
        Y = norm((B*Z*transpose(A)+transpose(B)*Z*A),'fro');
        X = B*Z*transpose(A)+transpose(B)*Z*A;
        Z = X/Y;
        if mod(k,2) == 0
            difference = abs(Z-Z_previouseven);
%             disp(difference);
            Z_previouseven = Z;
   
            if (difference < mu)
                break;
            end
        end
        k = k + 1;
    end
    return;
end



function [A] = hypergraph_to_extended2section(n,E)
    A = zeros(n,n);
    for k = 1:numel(E)
        if size(E{k},2) == 1
            A(cell2mat(E(k)), cell2mat(E(k))) = A(cell2mat(E(k)), cell2mat(E(k))) + 1;
        else
            p = perms(E{k});
            already_done = [];
            for i = 1:size(p,1)
                if isempty(intersect([p(i,1)], already_done))
                    for j = 2:size(p,2)
                        A(p(i,1),p(i,j)) = A(p(i,1),p(i,j)) + 1;
                    end
                    already_done = [already_done, p(i,1)];
                end
            end
                disp(A);
        end
    end
    return;
end



