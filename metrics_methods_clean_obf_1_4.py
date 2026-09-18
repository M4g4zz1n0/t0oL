_AS='identifier_reference';_AR='encapsulation';_AQ='index_bytes';_AP='storage_ratio';_AO='query_cost_weights';_AN='memory_bytes';_AM='working_set_fraction';_AL='intermediate';_AK='selectivity';_AJ='projection_paths';_AI='selection_paths';_AH='update';_AG='updates';_AF='update_workload';_AE='reference';_AD='set_attribute';_AC='operation';_AB='avg_document_storage_bytes';_AA='size_estimates';_A9='entries_per_document';_A8='document_count';_A7='items_kept';_A6='main_entities';_A5='identifier';_A4='avg_size_bytes';_A3='result_count';_A2='reached';_A1='source_entity';_A0='projection_attributes';_z='fields';_y='predicates';_x='min';_w='lookup';_v='avg_entry_storage_bytes';_u='evaluation';_t='after_entity';_s='to';_r='from';_q='path_statistics';_p='remote_fraction';_o='target_entity';_n='avg_item_size_bytes';_m='mongodb';_l='technology';_k='avg_distinct_targets';_j='phases';_i='kind';_h='stored_in';_g='references';_f='instances';_e='queries';_d='query_workload';_c='collections';_b='cardinality';_a='attribute';_Z='indexes';_Y='frequency';_X='into';_W='encapsulations';_V='max';_U='entries';_T='attributes';_S='target';_R='partition';_Q='items';_P='index';_O=True;_N='sides';_M='main_entity';_L='system';_K='documents';_J=False;_I='calculated';_H='relationships';_G='data_statistics';_F='collection';_E='entities';_D='name';_C='relationship';_B='entity';_A=None
def query_coverage(query):
	E=query;F=[];G=[];H=[];I=[]
	for A in E.get(_AI,[]):
		for B in range(len(A)):
			C=A[B].get(_B)
			if C not in F:F.append(C)
			if B>0:
				D=A[B].get(_C)
				if D not in H:H.append(D)
	for A in E.get(_AJ,[]):
		for B in range(len(A)):
			C=A[B].get(_B)
			if C not in G:G.append(C)
			if B>0:
				D=A[B].get(_C)
				if D not in I:I.append(D)
	return F,G,H,I,E.get(_o)
def query_impact(query,labeling):
	E,F,K,L,M=query_coverage(query);G=[];H=[];C=[]
	for B in labeling[_R]:
		for A in B['encapsulation_relationships']:
			if A not in C:C.append(A)
		for D in E:
			if D in B[_E]:G.append(B);break
		for D in F:
			if D in B[_E]:H.append(B);break
	I=[]
	for A in K:
		if A not in C:I.append(A)
	J=[]
	for A in L:
		if A not in C:J.append(A)
	return E,F,G,H,I,J,M
def single_query_cost(query,labeling,weights):
	Q=labeling;O=weights;R,S,B,C,H,I,J=query_impact(query,Q)
	if len(B)==0 or len(C)==0:return
	F=_A
	for T in Q[_R]:
		if J in T[_E]:F=T;break
	if F is _A:return
	P=O['scan'];K=O['unwind'];L=O[_w];M=K+L
	if len(B)==1 and len(C)==1 and B[0][_M]==C[0][_M]:
		if len(R)==1 and len(S)==1:
			if J==F[_M]:return P
			return K
		if J==F[_M]:return P
		A=len(H)+len(I);return K+A*M
	if J==F[_M]:N=P
	else:N=K
	if len(R)==1 and len(B)==1:
		D=len(H);A=len(C)-1;E=len(I)-A
		if E<0:return
		G=D+E;return N+G*M+A*L
	if len(S)==1 and len(C)==1:
		E=len(I);A=len(B)-1;D=len(H)-A
		if D<0:return
		G=D+E;return N+G*M+A*L
	D=len(H)-(len(B)-1);E=len(I)-(len(C)-1)
	if D<0 or E<0:return
	A=len(B)-1+(len(C)-1);G=D+E;return N+G*M+A*L
def query_max_cost(query,weights):
	A=weights;B,C,D,E,F=query_coverage(query)
	if len(B)==0 or len(C)==0:return
	return A['unwind']+(len(B)-1)*A[_w]+(len(C)-1)*A[_w]
def relationship_side(relationship,entity):
	A=relationship
	for B in range(len(A[_N])):
		if A[_N][B][_B]==entity:return B
def relationship_average(relationship_name,entity,er_relationships,relationship_stats):
	B=entity;A=relationship_name;C=er_relationships.get(A);F=relationship_stats.get(A,{})
	if C is _A:return
	G=relationship_side(C,B)
	if G is _A:return
	D=F.get(_N,[])
	if len(D)!=2:return
	for E in D:
		if E.get(_B)==B:return E.get('avg_connected')
def encapsulation_path(entity,root,parents):
	B=parents;C=[];A=entity
	while A!=root:
		if A not in B:return
		D,E=B[A];C.append((A,D,E));A=D
	return C
def workload_entity_contribution(entity,root,label,parents,er_relationships,relationship_stats,new_instances):
	I=relationship_stats;G=er_relationships;D=new_instances;C=label;B=root;A=entity
	if A==B:return 0
	if C=='X':return D[A]
	if C=='XL':return
	if C!='XR'and C!='XRL':return
	E=encapsulation_path(A,B,parents)
	if E is _A or len(E)==0:return
	J=_O
	for(K,H,F)in E:
		L=G[F];M=relationship_side(L,H)
		if M is _A:return
		N=L[_N][M][_b]
		if N[_x]!=1 or N[_V]!=1:J=_J;break
	if J:return D[B]
	O=1;P=1
	for(K,H,F)in E:
		Q=relationship_average(F,K,G,I);R=relationship_average(F,H,G,I)
		if Q is _A or R is _A:return
		O*=Q;P*=R
	return O*D[A]+P*D[B]
def entity_collection(labeling,entity):
	for A in labeling[_R]:
		if entity in A[_E]:return A[_M]
def predicate_for_entity(query,entity):
	A=_A
	for B in query.get(_y,[]):
		if B.get(_B)!=entity:continue
		if A is not _A:return
		A=B
	if A is _A:return{}
	return A
def query_index(name,data_system):
	for A in data_system.get(_Z,[]):
		if A.get(_D)==name:return A
def index_collection(index,labeling):
	A=_A
	for C in index.get(_z,[]):
		B=entity_collection(labeling,C.get(_B))
		if B is _A:return
		if A is _A:A=B
		elif B!=A:return
	return A
def index_has_field(index,entity,attribute):
	for A in index.get(_z,[]):
		if A.get(_B)==entity and A.get(_a)==attribute:return _O
	return _J
def usable_index(predicate,labeling,data_system):
	C=labeling;A=predicate
	if _P not in A:return
	B=query_index(A[_P],data_system)
	if B is _A:return
	if not index_has_field(B,A.get(_B),A.get(_a)):return
	if index_collection(B,C)!=entity_collection(C,A.get(_B)):return
	return B
def covering_index(index,query):
	B=query;A=index
	if A is _A or len(B.get(_A0,[]))==0:return _J
	for C in B.get(_y,[]):
		if not index_has_field(A,C.get(_B),C.get(_a)):return _J
	for D in B.get(_A0,[]):
		if not index_has_field(A,D.get(_B),D.get(_a)):return _J
	return _O
def encapsulation_direction(labeling,relationship_name):
	for A in labeling[_W]:
		if A[_C]==relationship_name:return A[_B],A[_X]
	return _A,_A
def traversal_factor(source,target,relationship_name,labeling,er_relationships,relationship_stats):
	D=relationship_name;C=target;B=labeling;A=source;E=entity_collection(B,A);F=entity_collection(B,C)
	if E is _A or F is _A:return
	if E==F:
		G,H=encapsulation_direction(B,D)
		if G==A and H==C:return 1
	return relationship_average(D,A,er_relationships,relationship_stats)
def selection_path(query):
	D=query;B=[]
	for K in D.get(_y,[]):
		A=K.get(_B)
		if A not in B:B.append(A)
	if len(B)==0:return[{_B:D.get(_o)}]
	C=_A
	for G in D.get(_AI,[]):
		E=[]
		for L in G:E.append(L.get(_B))
		H=_O
		for A in B:
			if A not in E:H=_J;break
		if not H:continue
		F=0
		for A in B:
			I=E.index(A)
			if I>F:F=I
		J=G[:F+1]
		if C is _A or len(J)<len(C):C=J
	return C
def access_first_collection(query,entity,labeling,data_system):
	I=data_system;H=labeling;G=query;C=entity;D=entity_collection(H,C);B=predicate_for_entity(G,C)
	if D is _A or B is _A:return
	A=I[_G][_E].get(D,{}).get(_f)
	if A is _A:return
	E=B.get(_AK,1);J=usable_index(B,H,I)
	if J is _A:F=A;K=A*E
	else:
		L=B.get('post_index_selectivity',1)
		if covering_index(J,G):F=0
		else:F=A*E
		K=A*E*L
	return{_B:C,_F:D,_K:F,_Q:K}
def access_relationship(query,source,target,relationship_name,current_items,remote_fraction,labeling,er_relationships,relationship_stats):
	E=relationship_name;C=labeling;B=source;A=target;F=traversal_factor(B,A,E,C,er_relationships,relationship_stats);G=predicate_for_entity(query,A)
	if F is _A or G is _A:return
	D=current_items*F;J=G.get(_AK,1);K=entity_collection(C,B);H=entity_collection(C,A)
	if K==H:I=0
	else:I=D
	return{_B:A,_F:H,_A1:B,_C:E,_A2:D,_p:remote_fraction,_K:I,_Q:D*J}
def project_relationship(source,target,relationship_name,current_items,remote_fraction,labeling,er_relationships,relationship_stats):
	E=relationship_name;C=labeling;B=target;A=source;F=traversal_factor(A,B,E,C,er_relationships,relationship_stats)
	if F is _A:return
	D=current_items*F;I=entity_collection(C,A);G=entity_collection(C,B)
	if I==G:H=0
	else:H=D
	return{_B:B,_F:G,_A1:A,_C:E,_A2:D,_p:remote_fraction,_K:H,_Q:D}
def query_phases(er_schema,data_system,labeling,query):
	c='estimated_result_cardinality';b='remote_fraction_if_separate';U=data_system;O=labeling;D=query;E=selection_path(D)
	if E is _A or len(E)==0:return
	P={}
	for V in er_schema[_H]:P[V[_D]]=V
	W=U[_G][_H];F=[];X=E[-1][_B];Q=access_first_collection(D,X,O,U)
	if Q is _A:return
	F.append(Q);G=Q[_Q];I=X
	for A in range(len(E)-1,0,-1):
		H=E[A-1][_B];M=E[A][_C];R=E[A].get(b);B=access_relationship(D,I,H,M,G,R,O,P,W)
		if B is _A:return
		F.append(B);G=B[_Q];I=H
	S=G;N={};Y=[];C=D.get(_AJ,[])
	for J in C:
		G=S;I=D[_o];Z=[]
		for A in range(1,len(J)):
			M=J[A][_C];H=J[A][_B];Z.append((M,H));K=tuple(Z)
			if K in N:G=N[K];I=H;continue
			R=J[A].get(b);B=project_relationship(I,H,M,G,R,O,P,W)
			if B is _A:return
			N[K]=B[_Q];Y.append(B);G=B[_Q];I=H
	F.extend(Y)
	if c in D:L=D[c]
	elif len(C)==1:
		if len(C[0])==1:L=S
		else:
			K=[]
			for A in range(1,len(C[0])):K.append((C[0][A][_C],C[0][A][_B]))
			L=N.get(tuple(K))
	else:
		a=_O
		for J in C:
			if len(J)!=1:a=_J;break
		if a:L=S
		else:L=_A
	if L is _A:return
	T=0
	if len(C)==1:
		for A in range(len(F)-1):T+=F[A][_Q]
	else:
		for B in F:T+=B[_Q]
	return{_j:F,_A3:L,_AL:T}
def average_attribute_values(attribute,statistics):
	A=attribute[_b]
	if A[_V]==1:return 1
	if A[_V]!='N'and A[_x]==A[_V]:return A[_V]
	return statistics.get('avg_values')
def average_attribute_size(attribute,statistics):
	A=statistics;B=A.get(_A4);C=average_attribute_values(attribute,A)
	if B is _A or C is _A:return
	return B*C
def entity_data_size(entity,entities,data_system):
	A=entity;B=0;E=data_system[_G][_E].get(A,{}).get(_T,{})
	for C in entities[A][_T]:
		D=average_attribute_size(C,E.get(C[_D],{}))
		if D is _A:return
		B+=D
	return B
def entity_attribute_size(entity,attribute_name,entities,data_system):
	B=attribute_name;A=entity;D=data_system[_G][_E].get(A,{}).get(_T,{})
	for C in entities.get(A,{}).get(_T,[]):
		if C[_D]==B:return average_attribute_size(C,D.get(B,{}))
def relationship_data_size(relationship,relationships,data_system):
	A=relationship;B=0;E=data_system[_G][_H].get(A,{}).get(_T,{})
	for C in relationships[A].get(_T,[]):
		D=average_attribute_size(C,E.get(C[_D],{}))
		if D is _A:return
		B+=D
	return B
def average_identifier_size(entity,entities,relationships,data_system,cache,path):
	L=data_system;K=relationships;F=entities;D=cache;B=path;A=entity
	if A in D:return D[A]
	if A in B:return
	B.append(A);E=0
	for G in F[A][_A5]:
		M=_J
		for N in F[A][_T]:
			if N[_D]!=G:continue
			P=L[_G][_E].get(A,{}).get(_T,{}).get(G,{});C=average_attribute_size(N,P)
			if C is _A:B.pop();return
			E+=C;M=_O;break
		if M:continue
		H=K.get(G)
		if H is _A:B.pop();return
		I=H[_N][0][_B];J=H[_N][1][_B]
		if I==J:B.pop();return
		if I==A:O=J
		elif J==A:O=I
		else:B.pop();return
		C=average_identifier_size(O,F,K,L,D,B)
		if C is _A:B.pop();return
		E+=C
	B.pop();D[A]=E;return E
def average_path_count(root,entity,parents,relationships,data_system):
	I=data_system;H=parents;G=entity;F=root
	if F==G:return 1
	A=G;D=[]
	while A!=F:
		if A not in H:return
		B,C=H[A];D.append((B,A,C));A=B
	D.reverse();J=[]
	for(B,M,C)in D:J.append(C)
	for E in I[_G].get(_q,[]):
		if E.get(_r)!=F or E.get(_s)!=G:continue
		if E.get(_H)==J:return E.get(_k)
	N=I[_G][_H];K=1
	for(B,M,C)in D:
		L=relationship_average(C,B,relationships,N)
		if L is _A:return
		K*=L
	return K
def collection_average_sizes(er_schema,data_system,labeling):
	R=er_schema;F=labeling;A=data_system;H={};C={};I={};X={};J={}
	for D in R[_E]:H[D[_D]]=D
	for K in R[_H]:C[K[_D]]=K
	for M in F[_W]:I[M[_B]]=M[_X],M[_C]
	for N in F[_R]:
		B=N[_M];E=entity_data_size(B,H,A)
		if E is _A:return
		if A[_L][_l][_D]==_m:E+=12
		for D in N[_E]:
			if D==B:continue
			O=average_path_count(B,D,I,C,A);S=entity_data_size(D,H,A)
			if O is _A or S is _A:return
			E+=O*S;K=I[D][1];G=relationship_data_size(K,C,A)
			if G is _A:return
			E+=O*G
		for L in F[_g]:
			P=L[_h]
			if P not in N[_E]:continue
			T=average_path_count(B,P,I,C,A);U=relationship_average(L[_C],P,C,A[_G][_H])
			if T is _A or U is _A:return
			V=L[_S]
			if V in F[_A6]and A[_L][_l][_D]==_m:Q=12
			else:Q=average_identifier_size(V,H,C,A,X,[])
			G=relationship_data_size(L[_C],C,A)
			if Q is _A or G is _A:return
			E+=T*U*(Q+G)
		J[B]=E
	for W in F.get(_I,{}).get(_c,[]):
		B=W[_F]
		if B in J:W['avg_document_bytes']=J[B]
	return J
def future_relationship_average(relationship_name,entity,relationships,data_system,horizon):
	Q='cardinality_limit';P='future_avg_connected';I=data_system;H=relationships;F=entity;E=relationship_name;J=relationship_average(E,F,H,I[_G][_H])
	if J is _A:return
	R=I[_G][_H].get(E,{});A=_A
	for K in R.get(_N,[]):
		if K.get(_B)==F:A=K;break
	if A is _A:return
	if P in A:B=A[P]
	else:
		L=A.get('growth_per_time_unit')
		if L is _A:return
		B=J+horizon*L
	if B<0:B=0
	C=[];G=H.get(E)
	if G is _A:return
	M=relationship_side(G,F)
	if M is _A:return
	N=G[_N][M][_b][_V]
	if N!='N':C.append(N)
	if A.get(Q)is not _A:C.append(A[Q])
	if len(C)>0:
		D=C[0]
		for O in C[1:]:
			if O<D:D=O
		if B>D:B=D
	return B
def future_path_count(root,entity,parents,relationships,data_system,horizon):
	N=relationships;M=parents;I=data_system;H=entity;G=root
	if G==H:return 1
	C=H;E=[]
	while C!=G:
		if C not in M:return
		A,B=M[C];E.append((A,C,B));C=A
	E.reverse();O=[]
	for(A,R,B)in E:O.append(B)
	J=_A
	for F in I[_G].get(_q,[]):
		if F.get(_r)!=G or F.get(_s)!=H:continue
		if F.get(_H)==O:J=F;break
	K=1;D=1
	for(A,R,B)in E:
		P=relationship_average(B,A,N,I[_G][_H]);Q=future_relationship_average(B,A,N,I,horizon)
		if P is _A or Q is _A:return
		K*=P;D*=Q
	if J is _A:return D
	L=J.get(_k)
	if L is _A:return D
	if K==0:
		if D==0:return L
		return
	return L*D/K
def collection_future_sizes(er_schema,data_system,labeling,horizon):
	R=er_schema;L=horizon;G=labeling;A=data_system;H={};B={};I={};X={};S={}
	for C in R[_E]:H[C[_D]]=C
	for J in R[_H]:B[J[_D]]=J
	for M in G[_W]:I[M[_B]]=M[_X],M[_C]
	for N in G[_R]:
		E=N[_M];D=entity_data_size(E,H,A)
		if D is _A:return
		if A[_L][_l][_D]==_m:D+=12
		for C in N[_E]:
			if C==E:continue
			O=future_path_count(E,C,I,B,A,L);T=entity_data_size(C,H,A)
			if O is _A or T is _A:return
			D+=O*T;J=I[C][1];F=relationship_data_size(J,B,A)
			if F is _A:return
			D+=O*F
		for K in G[_g]:
			P=K[_h]
			if P not in N[_E]:continue
			U=future_path_count(E,P,I,B,A,L);V=future_relationship_average(K[_C],P,B,A,L)
			if U is _A or V is _A:return
			W=K[_S]
			if W in G[_A6]and A[_L][_l][_D]==_m:Q=12
			else:Q=average_identifier_size(W,H,B,A,X,[])
			F=relationship_data_size(K[_C],B,A)
			if Q is _A or F is _A:return
			D+=U*V*(Q+F)
		S[E]=D
	return S
def temporary_operation_items(operation,phases):
	A=operation
	if _A7 in A:return A[_A7]
	D=A.get(_t);B=[]
	for C in phases:
		if C.get(_B)==D:B.append(C[_Q])
	if len(B)!=1:return
	return B[0]
def temporary_operation_size(operation,labeling,collection_sizes):
	A=operation
	if _n in A:return A[_n]
	B=entity_collection(labeling,A.get(_t))
	if B is _A:return
	return collection_sizes.get(B)
def average_result_size(query,er_schema,data_system,labeling,collection_sizes):
	H='estimated_avg_result_size_bytes';A=query
	if H in A:return A[H]
	B=A.get(_A0,[])
	if len(B)>0:
		C=0;D={}
		for E in er_schema[_E]:D[E[_D]]=E
		for F in B:
			G=entity_attribute_size(F[_B],F[_a],D,data_system)
			if G is _A:return
			C+=G
		return C
	I=entity_collection(labeling,A[_o]);return collection_sizes.get(I)
def reverse_path_count(entity,root,parents,relationships,data_system):
	I=data_system;H=parents;F=root;E=entity
	if E==F:return 1
	A=E;G=[]
	while A!=F:
		if A not in H:return
		C,B=H[A];G.append((A,C,B));A=C
	J=[]
	for(K,C,B)in G:J.append(B)
	for D in I[_G].get(_q,[]):
		if D.get(_r)!=E or D.get(_s)!=F:continue
		if D.get(_H)==J:return D.get(_k)
	N=I[_G][_H];L=1
	for(K,C,B)in G:
		M=relationship_average(B,K,relationships,N)
		if M is _A:return
		L*=M
	return L
def collection_working_fraction(block,data_system,parents,relationships):
	I=data_system;H=block;J=I[_G][_E];D=H[_M];A=J[D][_f]
	if A==0:return 0
	B=0
	for E in H[_E]:
		K=J.get(E,{});F=K.get(_f);G=K.get(_AM)
		if F is _A or G is _A:return
		if E==D:C=F*G
		else:
			L=reverse_path_count(E,D,parents,relationships,I)
			if L is _A:return
			C=F*G*L
		if C>A:C=A
		B+=C
	if B>A:B=A
	return B/A
def attribute_average_values(entity,attribute,er_schema,data_system):
	D=attribute;C=entity;B=_A
	for A in er_schema[_E]:
		if A[_D]==C:B=A;break
	if B is _A:return
	for A in B[_T]:
		if A[_D]!=D:continue
		E=data_system[_G][_E].get(C,{}).get(_T,{}).get(D,{});return average_attribute_values(A,E)
def index_entries_per_document(index,er_schema,data_system,labeling,parents,relationships):
	F=data_system;E=index;G=index_collection(E,labeling)
	if G is _A:return
	H=E.get(_z,[])
	if len(H)==0:return
	C=[];A=[];D=[]
	for I in H:
		B=I[_B];P=I[_a]
		if B not in C:C.append(B)
		J=average_path_count(G,B,parents,relationships,F);K=attribute_average_values(B,P,er_schema,F)
		if J is _A or K is _A:return
		A.append(J);D.append(K)
	if len(C)>1:
		for L in range(len(A)):
			if A[L]!=1 or D[L]!=1:return
		return 1
	M=0;N=1
	for O in D:
		if O>1:M+=1;N=O
	if M>1:return
	return A[0]*N
def index_entry_statistics(er_schema,data_system,labeling):
	H=data_system;G=er_schema;B=labeling;I={};J={};D={};K=[]
	for L in G[_H]:I[L[_D]]=L
	for E in B[_W]:J[E[_B]]=E[_X],E[_C]
	for A in B.get(_I,{}).get(_c,[]):D[A[_F]]=A.get(_A8)
	for C in H.get(_Z,[]):
		A=index_collection(C,B)
		if A is _A or A not in D:return
		M=D[A];N=C.get('participation_fraction');F=index_entries_per_document(C,G,H,B,J,I)
		if M is _A or N is _A or F is _A:return
		K.append({_P:C[_D],_F:A,_A9:F,_U:M*N*F})
	return K
def index_statistics(er_schema,data_system,labeling):
	B=data_system;C=index_entry_statistics(er_schema,B,labeling)
	if C is _A:return
	D=[]
	for A in C:
		E=query_index(A[_P],B)
		if E is _A:return
		F=E.get('avg_entry_memory_bytes')
		if F is _A:return
		D.append({_P:A[_P],_F:A[_F],_A9:A[_A9],_U:A[_U],_AN:A[_U]*F})
	return D
def tc_norm(er_schema,data_system,labeling):
	B=data_system;H=B[_d][_e];C=B[_u][_AO];D=0;A=0
	for E in H:
		F=single_query_cost(E,labeling,C);G=query_max_cost(E,C)
		if F is _A or G is _A:return
		D+=F;A+=G
	if A==0:return
	return D/A
def tc_w(er_schema,data_system,labeling):
	C=data_system;I=C[_d][_e];D=C[_u][_AO];E=0;A=0
	for B in I:
		F=single_query_cost(B,labeling,D);G=query_max_cost(B,D);H=B[_Y]
		if F is _A or G is _A:return
		E+=H*F;A+=H*G
	if A==0:return
	return E/A
def documents_ratio(er_schema,data_system,labeling):
	D=data_system;H=D[_d][_e];E=0;A=0
	for F in H:
		B=F[_Y]
		if B==0:continue
		C=query_phases(er_schema,D,labeling,F)
		if C is _A:return
		G=0
		for I in C[_j]:G+=I[_K]
		E+=B*G;A+=B*C[_A3]
	if A==0:return
	return E/A
def volume_ratio(er_schema,data_system,labeling):
	C=labeling;B=er_schema;A=data_system;N=A[_d][_e];D=collection_average_sizes(B,A,C)
	if D is _A:return
	J=0;E=0
	for F in N:
		G=F[_Y]
		if G==0:continue
		H=query_phases(B,A,C,F);K=average_result_size(F,B,A,C,D)
		if H is _A or K is _A:return
		L=0
		for I in H[_j]:
			if I[_K]==0:continue
			M=D.get(I[_F])
			if M is _A:return
			L+=I[_K]*M
		O=H[_A3]*K;J+=G*L;E+=G*O
	if E==0:return
	return J/E
def intermediate_results(er_schema,data_system,labeling):
	C=data_system;G=C[_d][_e];D=0;A=0
	for E in G:
		B=E[_Y]
		if B==0:continue
		F=query_phases(er_schema,C,labeling,E)
		if F is _A:return
		D+=B*F[_AL];A+=B
	if A==0:return
	return D/A
def working_set(er_schema,data_system,labeling):
	H=er_schema;B=labeling;A=data_system;I=collection_average_sizes(H,A,B);D=A[_L]['memory'].get('data_available_bytes');J=A[_L][_AA].get('memory_ratio')
	if I is _A or D is _A or D<=0 or J is _A:return
	K={};L={}
	for M in H[_H]:K[M[_D]]=M
	for E in B[_W]:L[E[_B]]=E[_X],E[_C]
	N=0
	for O in B[_R]:
		F=O[_M];P=A[_G][_E][F].get(_f);G=collection_working_fraction(O,A,L,K);Q=I.get(F)
		if P is _A or G is _A or Q is _A:return
		R=Q*J;S=P*G*R;N+=S
		for C in B.get(_I,{}).get(_c,[]):
			if C[_F]==F:C[_AM]=G;C['avg_document_memory_bytes']=R;C['working_set_bytes']=S;break
	return N/D
def index_memory(er_schema,data_system,labeling):
	B=labeling;A=data_system;F=A.get(_Z,[])
	if len(F)==0:B.setdefault(_I,{})[_Z]=[];return 0
	C=A[_L]['memory'].get('index_available_bytes')
	if C is _A or C<=0:return
	D=index_statistics(er_schema,A,B)
	if D is _A:return
	E=0
	for G in D:E+=G[_AN]
	B.setdefault(_I,{})[_Z]=D;return E/C
def temporary_storage(er_schema,data_system,labeling):
	S='type';R='temporary_storage';M=er_schema;D=labeling;C=data_system;T=C[_d][_e];U=C[_L].get(R,{});H=U.get('memory_limit_bytes');I=0;N=[]
	for E in T:
		if E[_Y]<=0:continue
		O=E.get('temporary_operations',[])
		if len(O)==0:continue
		if H is _A or H<=0:return
		F=_A;B=_A;G=0
		for A in O:
			if _A7 not in A:
				if F is _A:
					P=query_phases(M,C,D,E)
					if P is _A:return
					F=P[_j]
			if _n not in A:
				if B is _A:
					B=collection_average_sizes(M,C,D)
					if B is _A:return
			J=temporary_operation_items(A,F if F is not _A else[]);K=temporary_operation_size(A,D,B if B is not _A else{})
			if J is _A or K is _A:return
			Q=J*K;L=Q/H
			if L>G:G=L
			N.append({'query':E[_D],S:A[S],_t:A[_t],_Q:J,_n:K,'temporary_bytes':Q,'risk':L})
		if G>I:I=G
	D.setdefault(_I,{})[R]=N;return I
def document_margin(er_schema,data_system,labeling):
	B=labeling.get(_I,{}).get(_c)
	if B is _A or len(B)==0:return
	A=_A
	for D in B:
		C=D.get('document_margin')
		if C is _A:return
		if A is _A or C<A:A=C
	return A
def document_growth(er_schema,data_system,labeling):
	J=er_schema;D=data_system;B=labeling;E=D[_u].get('planning_horizon')
	if E is _A or E<0:return
	K=collection_average_sizes(J,D,B);L=collection_future_sizes(J,D,B,E)
	if K is _A or L is _A:return
	F=0
	for M in B[_R]:
		G=M[_M];C=K.get(G);H=L.get(G)
		if C is _A or H is _A or C<=0:return
		A=(H-C)/C
		if A<0:A=0
		if A>F:F=A
		for I in B.get(_I,{}).get(_c,[]):
			if I[_F]==G:I['future_avg_document_bytes']=H;I['document_growth']=A;break
	return F
def network_volume(er_schema,data_system,labeling):
	T='network_transfers';K=er_schema;C=data_system;B=labeling;L=C[_L].get('distribution',{}).get('nodes')
	if L is _A:return
	if L==1:B.setdefault(_I,{})[T]=[];return 0
	M=collection_average_sizes(K,C,B)
	if M is _A:return
	N=0;E=0;O=[]
	for F in C[_d][_e]:
		G=F[_Y]
		if G<=0:continue
		P=query_phases(K,C,B,F)
		if P is _A:return
		Q=0
		for A in P[_j]:
			if _C not in A:continue
			R=entity_collection(B,A[_A1]);H=A[_F]
			if R==H:continue
			I=A.get(_p);D=A.get(_A2);J=M.get(H)
			if I is _A or D is _A or J is _A:return
			D*=I;S=D*J;Q+=S;O.append({'query':F[_D],_C:A[_C],'from_collection':R,'to_collection':H,_p:I,_Q:D,_n:J,'network_bytes':S})
		N+=G*Q;E+=G
	if E==0:return
	B.setdefault(_I,{})[T]=O;return N/E
def storage_space(er_schema,data_system,labeling):
	Z='copies';L=er_schema;K='storage_bytes';D=labeling;A=data_system;M=A[_L].get(_AA,{}).get(_AP);N=A[_L].get('replication',{});O=N.get('document_replicas')
	if M is _A or O is _A:return
	P=collection_average_sizes(L,A,D)
	if P is _A:return
	Q=1+O;F=0;R=[]
	for E in D.get(_I,{}).get(_c,[]):
		S=E[_F];G=E.get(_A8);T=P.get(S)
		if G is _A or T is _A:return
		H=T*M;B=G*H*Q;F+=B;E[_AB]=H;E[K]=B;R.append({_F:S,_K:G,_AB:H,Z:Q,K:B})
	a=A.get(_Z,[]);I=0;U=[]
	if len(a)>0:
		V=N.get('index_replicas')
		if V is _A:return
		W=index_entry_statistics(L,A,D)
		if W is _A:return
		X=1+V
		for C in W:
			Y=query_index(C[_P],A)
			if Y is _A:return
			J=Y.get(_v)
			if J is _A:return
			B=C[_U]*J*X;I+=B;U.append({_P:C[_P],_F:C[_F],_U:C[_U],_v:J,Z:X,K:B})
	D.setdefault(_I,{})['storage']={_K:R,_Z:U,'document_bytes':F,_AQ:I};return F+I
def tw_norm(er_schema,data_system,labeling):
	F=data_system;E=er_schema;A=labeling;T=F[_G][_E];U=F[_G][_H];G={};C={};H={};I={}
	for J in E[_H]:G[J[_D]]=J
	for B in E[_E]:K=B[_D];C[K]=T[K]['new_instances_per_time_unit']
	for L in A['entity_labels']:H[L[_B]]=L['label']
	for D in A[_W]:I[D[_B]]=D[_X],D[_C]
	M=0
	for N in A[_R]:
		O=N[_M];P=C[O];Q=0
		for B in N[_E]:
			R=workload_entity_contribution(B,O,H[B],I,G,U,C)
			if R is _A:return
			Q+=R
		S=Q+P
		if S==0:return
		M+=P/S
	if len(A[_R])==0:return
	return M/len(A[_R])
def prepare_update_data(er_schema,labeling):
	B=er_schema;C={};D={};E={}
	for F in B[_E]:C[F[_D]]=F
	for G in B[_H]:D[G[_D]]=G
	for A in labeling[_W]:E[A[_B]]=A[_X],A[_C]
	return C,D,E
def update_path_statistic(entity,root,parents,data_system):
	C=entity;A=encapsulation_path(C,root,parents)
	if A is _A:return _A,_A
	D=[]
	for(F,G,E)in A:D.append(E)
	for B in data_system[_G].get(_q,[]):
		if B.get(_r)!=C or B.get(_s)!=root:continue
		if B.get(_H)==D:return B,A
	return _A,A
def update_path_count(entity,root,parents,relationships,data_system):
	H=data_system;G=entity;D=relationships
	if G==root:return 1
	E,B=update_path_statistic(G,root,parents,H)
	if B is _A or len(B)==0:return
	if E is not _A and E.get(_k)is not _A:return E[_k]
	I=H[_G][_H]
	if len(B)==1:C,F,A=B[0];return relationship_average(A,C,D,I)
	J=_J
	for(C,F,O)in B:
		A=D[O];K=relationship_side(A,C);L=relationship_side(A,F)
		if K is _A or L is _A:return
		P=A[_N][K][_b][_V];Q=A[_N][L][_b][_V]
		if J and Q!=1:return
		if P!=1:J=_O
	M=1
	for(C,F,A)in B:
		N=relationship_average(A,C,D,I)
		if N is _A:return
		M*=N
	return M
def update_path_multi_probability(entity,root,parents,relationships,data_system):
	F='probability_multiple_targets';C=entity
	if C==root:return 0
	A,B=update_path_statistic(C,root,parents,data_system)
	if B is _A or len(B)==0:return
	if A is not _A and A.get(F)is not _A:return A[F]
	for(G,J,H)in B:
		D=relationships[H];E=relationship_side(D,G)
		if E is _A:return
		I=D[_N][E][_b][_V]
		if I!=1:return
	return 0
def update_path_always_present(entity,root,parents,relationships,data_system):
	F='probability_zero_targets';C=entity
	if C==root:return _O
	A,B=update_path_statistic(C,root,parents,data_system)
	if B is _A or len(B)==0:return _J
	if A is not _A and A.get(F)is not _A:return A[F]==0
	for(G,J,H)in B:
		D=relationships[H];E=relationship_side(D,G)
		if E is _A:return _J
		I=D[_N][E][_b][_x]
		if I==0:return _J
	return _O
def add_update_contribution(contributions,collection,entity,documents,kind,relationship=_A,target=_A):
	E=target;D=relationship;C=documents;B=collection
	if B is _A or C is _A:return _J
	A={_F:B,_B:entity,_K:C,_i:kind}
	if D is not _A:A[_C]=D
	if E is not _A:A[_S]=E
	contributions.append(A);return _O
def update_contributions(er_schema,data_system,labeling,update):
	O=update;K=data_system;D=labeling;E=D.setdefault(_I,{}).setdefault('update_contributions',{});F=O.get(_D)
	if F in E:return E[F]
	P,L,M=prepare_update_data(er_schema,D);I=[];U=O[_AC];Q=O[_S]
	if U==_AD:
		G=Q[_B];A=entity_collection(D,G);H=update_path_count(G,A,M,L,K)
		if not add_update_contribution(I,A,G,H,_B):E[F]=_A;return
		if Q[_a]in P[G][_A5]:
			for C in D[_g]:
				if C[_S]!=G:continue
				B=C[_h];A=entity_collection(D,B);H=update_path_count(B,A,M,L,K)
				if not add_update_contribution(I,A,B,H,_AE,C[_C],G):E[F]=_A;return
	else:
		J=Q[_C];N=_A
		for R in D[_W]:
			if R[_C]==J:N=R;break
		if N is not _A:
			B=N[_X];A=entity_collection(D,B);H=update_path_count(B,A,M,L,K)
			if not add_update_contribution(I,A,B,H,_AR,J,N[_B]):E[F]=_A;return
		else:
			S=_J
			for C in D[_g]:
				if C[_C]!=J:continue
				S=_O;B=C[_h];A=entity_collection(D,B);H=update_path_count(B,A,M,L,K)
				if not add_update_contribution(I,A,B,H,_AE,J,C[_S]):E[F]=_A;return
			if not S:E[F]=_A;return
		for G in P:
			if J not in P[G][_A5]:continue
			for C in D[_g]:
				if C[_S]!=G:continue
				if C[_C]==J:continue
				B=C[_h];A=entity_collection(D,B);H=update_path_count(B,A,M,L,K)
				if not add_update_contribution(I,A,B,H,_AS,C[_C],G):E[F]=_A;return
	T=[]
	for V in I:
		A=V[_F]
		if A in T:E[F]=_A;return
		T.append(A)
	E[F]=I;return I
def update_identifier_size(entity,entities,relationships,data_system,labeling,cache):
	B=data_system;A=entity
	if A in labeling[_A6]and B[_L][_l][_D]==_m:return 12
	return average_identifier_size(A,entities,relationships,B,cache,[])
def entity_update_size(entity,entities,relationships,data_system,labeling,identifier_cache,entity_cache,path):
	M=identifier_cache;K=entities;I=entity_cache;H=labeling;D=relationships;C=path;B=data_system;A=entity
	if A in I:return I[A]
	if A in C:return
	C.append(A);E=entity_data_size(A,K,B)
	if E is _A:C.pop();return
	for L in H[_W]:
		if L[_X]!=A:continue
		Q=L[_B];N=L[_C];F=relationship_average(N,A,D,B[_G][_H]);O=entity_update_size(Q,K,D,B,H,M,I,C);G=relationship_data_size(N,D,B)
		if F is _A or O is _A or G is _A:C.pop();return
		E+=F*(O+G)
	for J in H[_g]:
		if J[_h]!=A:continue
		F=relationship_average(J[_C],A,D,B[_G][_H]);P=update_identifier_size(J[_S],K,D,B,H,M);G=relationship_data_size(J[_C],D,B)
		if F is _A or P is _A or G is _A:C.pop();return
		E+=F*(P+G)
	C.pop();I[A]=E;return E
def contribution_representation_size(contribution,entities,relationships,data_system,labeling,identifier_cache,entity_cache):
	H=entity_cache;G=identifier_cache;F=labeling;E=entities;C=data_system;B=relationships;A=contribution
	if A[_i]==_B:return entity_update_size(A[_B],E,B,C,F,G,H,[])
	if A[_i]==_AR:
		I=entity_update_size(A[_S],E,B,C,F,G,H,[]);D=relationship_data_size(A[_C],B,C)
		if I is _A or D is _A:return
		return I+D
	if A[_i]==_AE or A[_i]==_AS:
		J=update_identifier_size(A[_S],E,B,C,F,G);D=relationship_data_size(A[_C],B,C)
		if J is _A or D is _A:return
		return J+D
def update_modified_size(update,data_system,contributions,entities,relationships,labeling,identifier_cache,entity_cache):
	C='avg_modified_size_bytes';B=update
	if B.get(_AC)==_AD:
		if C in B:A=B[C]
		else:D=B[_S];A=entity_attribute_size(D[_B],D[_a],entities,data_system)
		if A is _A or A<=0:return
		return A
	A=B.get(C)
	if A is _A or A<=0:return
	return A
def update_write_size(update,contribution,modified,entities,relationships,data_system,labeling,collection_sizes,identifier_cache,entity_cache):
	K='subdocument';J='field';I=entity_cache;H=identifier_cache;G=labeling;F=data_system;E=relationships;D=entities;C=update;B=contribution;A=C['granularity']
	if A=='document':return collection_sizes.get(B[_F])
	if C.get(_AC)==_AD and B[_i]==_B:
		if A==J:return modified
		if A==K:return entity_update_size(B[_B],D,E,F,G,H,I,[])
		return
	if A==J or A==K:return contribution_representation_size(B,D,E,F,G,H,I)
def contribution_multi_probability(contribution,parents,relationships,data_system):A=contribution;return update_path_multi_probability(A[_B],A[_F],parents,relationships,data_system)
def contribution_always_present(contribution,parents,relationships,data_system):A=contribution;return update_path_always_present(A[_B],A[_F],parents,relationships,data_system)
def update_documents(er_schema,data_system,labeling):
	G=labeling;F=data_system;H=0;A=0;I=[]
	for B in F[_AF][_AG]:
		C=B[_Y]
		if C<=0:continue
		D=update_contributions(er_schema,F,G,B)
		if D is _A:return
		E=0
		for J in D:E+=J[_K]
		I.append({_AH:B[_D],_K:E,'contributions':D});H+=C*E;A+=C
	if A==0:return
	G.setdefault(_I,{})['update_documents']=I;return H/A
def rewrite_ratio(er_schema,data_system,labeling):
	E=er_schema;B=data_system;A=labeling;J=collection_average_sizes(E,B,A)
	if J is _A:return
	K,L,S=prepare_update_data(E,A);M={};N={};O=0;F=0;P=[]
	for C in B[_AF][_AG]:
		G=C[_Y]
		if G<=0:continue
		H=update_contributions(E,B,A,C)
		if H is _A:return
		D=update_modified_size(C,B,H,K,L,A,M,N)
		if D is _A:return
		I=0
		for Q in H:
			R=update_write_size(C,Q,D,K,L,B,A,J,M,N)
			if R is _A:return
			I+=Q[_K]*R
		P.append({_AH:C[_D],'modified_bytes':D,'rewritten_bytes':I});O+=G*I;F+=G*D
	if F==0:return
	A.setdefault(_I,{})['rewrite_updates']=P;return O/F
def multi_document_updates(er_schema,data_system,labeling):
	H=er_schema;D=labeling;C=data_system;N,I,J=prepare_update_data(H,D);K=0;E=0;L=[]
	for F in C[_AF][_AG]:
		G=F[_Y]
		if G<=0:continue
		A=update_contributions(H,C,D,F)
		if A is _A or len(A)==0:return
		if len(A)==1:B=contribution_multi_probability(A[0],J,I,C)
		else:
			B=1
			for M in A:
				if not contribution_always_present(M,J,I,C):B=_A;break
		if B is _A:return
		L.append({_AH:F[_D],'probability_multi_document':B});K+=G*B;E+=G
	if E==0:return
	D.setdefault(_I,{})['multi_document_updates']=L;return K/E
def lifecycle_volume(er_schema,data_system,labeling):
	g='read_bytes';f='write_bytes';R=er_schema;Q='migration';C=labeling;B=data_system;G=B[_u].get('lifecycle_scenario');S=B[_L].get(_AA,{}).get(_AP)
	if G not in['create',Q]or S is _A:return
	T=collection_average_sizes(R,B,C)
	if T is _A:return
	H=0;U=[]
	for V in C.get(_I,{}).get(_c,[]):
		W=V[_F];I=V.get(_A8);X=T.get(W)
		if I is _A or X is _A:return
		Y=X*S;A=I*Y;H+=A;U.append({_F:W,_K:I,_AB:Y,f:A})
	J=0;Z=[];h=B.get(_Z,[])
	if len(h)>0:
		a=index_entry_statistics(R,B,C)
		if a is _A:return
		for D in a:
			b=query_index(D[_P],B)
			if b is _A:return
			K=b.get(_v)
			if K is _A:return
			A=D[_U]*K;J+=A;Z.append({_P:D[_P],_F:D[_F],_U:D[_U],_v:K,'build_bytes':A})
	L=0;c=[]
	if G==Q:
		M=B.get(Q)
		if not isinstance(M,dict)or M.get('mode')!='full_rebuild':return
		N=[]
		for i in C[_R]:
			for E in i[_E]:
				if E not in N:N.append(E)
		for F in M.get('source_structures',[]):
			d=_J
			for E in F.get('maps_to',[]):
				if E in N:d=_O;break
			if not d:continue
			O=F.get(_f);P=F.get(_A4)
			if O is _A or P is _A:return
			A=O*P;L+=A;c.append({'source':F[_D],_f:O,_A4:P,g:A})
	e=L+H+J;C.setdefault(_I,{})['lifecycle']={'scenario':G,'source_reads':c,'collection_writes':U,'index_builds':Z,g:L,f:H,_AQ:J,'total_bytes':e};return e