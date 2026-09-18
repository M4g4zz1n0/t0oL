_AD='evaluation_results.json';_AC='not_verifiable';_AB='document_size';_AA='information_loss';_A9='beam_width';_A8='main_sets';_A7='instances';_A6='query_workload';_A5='evaluable';_A4='collections';_A3='calculated';_A2='utf-8';_A1='allow_information_loss';_A0='cardinality_limit';_z='into';_y='main_entity';_x='recommended';_w='format_version';_v='schema';_u='document_margin';_t='entity_stats';_s='relationship_stats';_r='couchbase';_q='evaluation';_p='XRL';_o='min';_n='candidate_id';_m='parent_relationships';_l='parents';_k='role';_j='collection';_i='mongodb';_h='system';_g='data_statistics';_f='cardinality';_e='metrics';_d='attributes';_c='technology';_b='max';_a='labeling';_Z='id';_Y='ratio';_X='order_key';_W='target_role';_V='entity_labels';_U='stored_role';_T='main_entities';_S='partition';_R='stored_in';_Q='encapsulations';_P='target';_O='label';_N='name';_M='entities';_L='growth_cost';_K='storage_cost';_J='relationships';_I='references';_H='query_score';_G=True;_F='relationship';_E=False;_D='penalty';_C='entity';_B='sides';_A=None;import sys,os,json;from collections import deque;from input_checks_clean_1_4 import read_json,check_er_schema,check_labeled_schema,check_data_system,check_metric_data,check_labeled_technology;from metrics_methods_clean_obf_1_4 import tc_norm,tc_w,documents_ratio,volume_ratio,intermediate_results,working_set,index_memory,temporary_storage,document_margin,document_growth,network_volume,storage_space,tw_norm,update_documents,rewrite_ratio,multi_document_updates,lifecycle_volume,relationship_average;metrics=['Costo normalizzato delle query (TC_norm)','Costo delle query pesato sul workload (TC_w)','Documenti esaminati / risultati restituiti','Volume esaminato / volume restituito','Cardinalità complessiva dei risultati intermedi','Working set / memoria disponibile','Dimensione indici / memoria disponibile','Rischio storage temporaneo','Margine dimensione massima documenti','Rischio di crescita dei documenti','Volume trasferito tra nodi','Spazio di memorizzazione richiesto','Punteggio normalizzato storage/workload (TW_norm)','Documenti coinvolti negli aggiornamenti','Volume riscritto / volume modificato','Incidenza aggiornamenti multi-documento','Volume creazione o migrazione']
def print_menu():
	print('\n==================== METRICHE ====================');print('\nQUERY')
	for A in range(5):print(f"{A+1:2}. {metrics[A]}")
	print('\nMEMORIA / FISICO')
	for A in range(5,12):print(f"{A+1:2}. {metrics[A]}")
	print('\nAGGIORNAMENTI')
	for A in range(12,16):print(f"{A+1:2}. {metrics[A]}")
	print('\nLIFECYCLE');print(f"17. {metrics[16]}");print('==================================================')
def choose_metrics():
	while _G:
		print_menu();F=input('\nSeleziona 5 metriche, separate da spazio o virgola: ').strip();D=F.replace(',',' ').split()
		if len(D)!=5:print('\nDevono essere selezionate esattamente 5 metriche.');continue
		B=[];C=_G
		for E in D:
			if not E.isdigit():C=_E;break
			A=int(E)
			if A<1 or A>17 or A in B:C=_E;break
			B.append(A)
		if not C:print('\nLe metriche devono essere 5 numeri distinti compresi tra 1 e 17.');continue
		return B
def choose_evaluation_metrics():
	while _G:
		print_menu();D=input('\nSeleziona le metriche da valutare, oppure premi Invio per tutte: ').strip()
		if not D:
			A=[]
			for B in range(1,18):A.append(B)
			return A
		F=D.replace(',',' ').split();A=[];C=_G
		for E in F:
			if not E.isdigit():C=_E;break
			B=int(E)
			if B<1 or B>17 or B in A:C=_E;break
			A.append(B)
		if not C or len(A)==0:print('\nLe metriche devono essere numeri distinti compresi tra 1 e 17.');continue
		return A
def schema_graph(er_schema):
	F=er_schema;G=[];H={};B={}
	for I in F[_M]:A=I[_N];G.append(A);B[A]=[]
	for C in F[_J]:
		A=C[_N];H[A]=C;D=C[_B][0][_C];E=C[_B][1][_C]
		if D==E:continue
		B[D].append((A,E));B[E].append((A,D))
	return G,H,B
def connected_components(entities,adjacent):
	D=[];A=[]
	for E in entities:
		if E in A:continue
		F=[];C=[E]
		while C:
			B=C.pop()
			if B in A:continue
			A.append(B);F.append(B)
			for(H,G)in adjacent[B]:
				if G not in A:C.append(G)
		D.append(F)
	return D
def main_entity_sets(entities,components):
	A=entities;C=[]
	for G in range(1,1<<len(A)):
		B=[]
		for D in range(len(A)):
			if G&1<<D:B.append(A[D])
		E=_G
		for H in components:
			F=_E
			for I in H:
				if I in B:F=_G;break
			if not F:E=_E;break
		if E:C.append(B)
	return C
def distances_from_main(main_entities,adjacent):
	A={};B=deque()
	for D in main_entities:A[D]=0;B.append(D)
	while B:
		E=B.popleft()
		for(F,C)in adjacent[E]:
			if C not in A:A[C]=A[E]+1;B.append(C)
	return A
def cardinality_label(cardinality):
	A=cardinality
	if A[_b]==1:
		if A[_o]==0:return'XL'
		return'X'
	if A[_o]==0:return _p
	return'XR'
def build_labels(entities,main_entities,relationships,distances,parents,parent_relationships):
	G=main_entities;F=entities;D=distances;B={}
	for A in G:B[A]=A
	E=0
	for A in D:E=max(E,D[A])
	for L in range(1,E+1):
		for A in F:
			if D[A]!=L:continue
			H=parents[A];M=relationships[parent_relationships[A]];C=_A
			for I in M[_B]:
				if I[_C]==A:C=I[_f];break
			J=cardinality_label(C)
			if H not in G and C[_o]==1 and C[_b]==1:J=B[H]
			B[A]=J
	K=[]
	for A in F:K.append({_C:A,_O:B[A]})
	return K
def build_partition(entities,main_entities,parents,parent_relationships):
	G='encapsulation_relationships';E=parents;C=main_entities;D={}
	for A in C:D[A]={_j:A,_y:A,_M:[],G:[]}
	for A in entities:
		B=A
		while B not in C:B=E[B]
		D[B][_M].append(A)
	for A in E:
		B=A
		while B not in C:B=E[B]
		D[B][G].append(parent_relationships[A])
	F=[]
	for A in C:F.append(D[A])
	return F
def reference_label(target,main_entities):
	if target in main_entities:return _Z
	return'key'
def add_reference_variants(remaining,pos,references,main_entities,relationships,base_labeling,labelings):
	J=relationships;I=labelings;H=pos;G=remaining;E=base_labeling;B=main_entities;A=references
	if H==len(G):P={_Z:f"L{len(I)+1:06d}",_T:E[_T][:],_V:E[_V][:],_Q:E[_Q][:],_I:A[:],_S:E[_S]};I.append(P);return
	F=G[H];L=J[F];C=L[_B][0][_C];D=L[_B][1][_C]
	if C==D:M=L[_B][0].get(_k);N=L[_B][1].get(_k);K=reference_label(D,B);O={_F:F,_R:C,_P:D,_O:K,_U:M,_W:N};A.append(O);add_reference_variants(G,H+1,A,B,J,E,I);A.pop();K=reference_label(C,B);O={_F:F,_R:D,_P:C,_O:K,_U:N,_W:M};A.append(O);add_reference_variants(G,H+1,A,B,J,E,I);A.pop();A.append({_F:F,_R:C,_P:D,_O:reference_label(D,B),_U:M,_W:N});A.append({_F:F,_R:D,_P:C,_O:reference_label(C,B),_U:N,_W:M});add_reference_variants(G,H+1,A,B,J,E,I);A.pop();A.pop();return
	K=reference_label(D,B);A.append({_F:F,_R:C,_P:D,_O:K});add_reference_variants(G,H+1,A,B,J,E,I);A.pop();K=reference_label(C,B);A.append({_F:F,_R:D,_P:C,_O:K});add_reference_variants(G,H+1,A,B,J,E,I);A.pop();A.append({_F:F,_R:C,_P:D,_O:reference_label(D,B)});A.append({_F:F,_R:D,_P:C,_O:reference_label(C,B)});add_reference_variants(G,H+1,A,B,J,E,I);A.pop();A.pop()
def add_encapsulations(non_main,pos,main_entities,entities,relationships,adjacent,distances,parents,parent_relationships,encapsulations,labelings):
	M=labelings;L=adjacent;J=entities;I=pos;H=non_main;G=distances;F=relationships;E=encapsulations;D=parent_relationships;C=parents;B=main_entities
	if I==len(H):
		R=build_labels(J,B,F,G,C,D);S=build_partition(J,B,C,D);N=[]
		for T in E:N.append(T[_F])
		O=[]
		for P in F:
			if P not in N:O.append(P)
		U={_T:B,_V:R,_Q:E[:],_S:S};add_reference_variants(O,0,[],B,F,U,M);return
	A=H[I]
	for(Q,K)in L[A]:
		if G[K]!=G[A]-1:continue
		C[A]=K;D[A]=Q;E.append({_F:Q,_C:A,_z:K});add_encapsulations(H,I+1,B,J,F,L,G,C,D,E,M);E.pop();del C[A];del D[A]
def generate_labelings(er_schema):
	A,I,D=schema_graph(er_schema);J=connected_components(A,D);K=main_entity_sets(A,J);F=[]
	for G in K:
		B=distances_from_main(G,D);H=[];E=0
		for C in B:E=max(E,B[C])
		for L in range(1,E+1):
			for C in A:
				if B[C]==L:H.append(C)
		add_encapsulations(H,0,G,A,I,D,B,{},{},[],F)
	return F
exact_entity_limit=8;guided_main_pivots=6;guided_beam_width=24;guided_reference_width=48;guided_reference_exact_limit=5
def guided_workload_scores(er_schema,data_system):
	Y='frequency';T=data_system;S=er_schema;C={};L={};D={};M=[]
	for A in S[_M]:H=A[_N];C[H]=0;D[H]=0
	U={}
	for B in S[_J]:H=B[_N];U[H]=B;L[H]=0
	for I in T[_A6]['queries']:
		E=I.get(Y,0)
		if E<=0:continue
		F=I.get('target_entity')
		if F not in M:M.append(F)
		N=[];O=[];P=[]
		for G in I.get('selection_paths',[]):P.append(G)
		for G in I.get('projection_paths',[]):P.append(G)
		for G in P:
			for Q in range(len(G)):
				A=G[Q].get(_C)
				if A not in N:N.append(A)
				if Q==0:continue
				B=G[Q].get(_F)
				if B not in O:O.append(B)
		for A in N:C[A]+=E
		if F in C:C[F]+=E
		for B in O:L[B]+=E
	for R in T.get('update_workload',{}).get('updates',[]):
		E=R.get(Y,0)
		if E<=0:continue
		F=R.get(_P,{});Z=R.get('operation')
		if Z=='set_attribute':
			A=F.get(_C)
			if A in D:D[A]+=E
			continue
		a=F.get(_F);B=U.get(a)
		if B is _A:continue
		for b in B[_B]:
			A=b[_C]
			if A in D:D[A]+=E
	J=0;K=0
	for A in C:
		if C[A]>J:J=C[A]
		if D[A]>K:K=D[A]
	V={}
	for A in C:
		W=0;X=0
		if J>0:W=C[A]/J
		if K>0:X=D[A]/K
		V[A]=W+X
	return V,L,D,M
def guided_entity_better(first,second,entity_scores,adjacent):
	D=adjacent;C=entity_scores;B=second;A=first
	if C[A]>C[B]:return _G
	if C[A]<C[B]:return _E
	if len(D[A])>len(D[B]):return _G
	if len(D[A])<len(D[B]):return _E
	return A<B
def guided_entity_order(component,entity_scores,adjacent):
	A=component[:];C=[]
	while len(A)>0:
		B=A[0]
		for D in A[1:]:
			if guided_entity_better(D,B,entity_scores,adjacent):B=D
		C.append(B);A.remove(B)
	return C
def valid_main_set(main_entities,components):
	A=main_entities
	if len(A)==0:return _E
	for C in components:
		B=_E
		for D in C:
			if D in A:B=_G;break
		if not B:return _E
	return _G
def add_guided_main_set(sets,main_entities,entities,components):
	A=[]
	for B in sorted(entities):
		if B in main_entities:A.append(B)
	if not valid_main_set(A,components):return
	for C in sets:
		if C==A:return
	sets.append(A)
def guided_main_entity_sets(entities,components,adjacent,entity_scores,targets,pivots_count):
	H=pivots_count;G=adjacent;E=entity_scores;D=components;C=entities;I=guided_entity_order(C,E,G);A=[];Q=guided_entity_order(targets,E,G)
	for B in Q:
		if B not in A:
			A.append(B)
			if len(A)==H:break
	if len(A)<H:
		for B in I:
			if B in A:continue
			A.append(B)
			if len(A)==H:break
	J=[]
	for K in D:
		L=_E
		for B in K:
			if B in A:L=_G;break
		if L:continue
		M=guided_entity_order(K,E,G)
		if len(M)>0:J.append(M[0])
	F=[];R=1<<len(A)
	for S in range(R):
		N=J[:]
		for O in range(len(A)):
			if S&1<<O:N.append(A[O])
		add_guided_main_set(F,N,C,D)
	P=[]
	for B in I:
		if E[B]>0:P.append(B)
	add_guided_main_set(F,P,C,D);add_guided_main_set(F,C,C,D);return F
def state_signature(state):return state.get(_X,'')
def add_unique_state(result,state,seen):
	A=state;B=state_signature(A)
	if B in seen:return _E
	seen.add(B);result.append(A);return _G
def query_state_key(state):A=state;return-A[_H],A[_D],state_signature(A)
def penalty_state_key(state):A=state;return A[_D],-A[_H],state_signature(A)
def prune_guided_states(states,width):
	D=width;A=states
	if len(A)<=D:return A
	E=A[:];F=A[:];E.sort(key=query_state_key);F.sort(key=penalty_state_key);B=[];G=set();C=0
	while len(B)<D and C<len(A):
		add_unique_state(B,E[C],G)
		if len(B)==D:break
		add_unique_state(B,F[C],G);C+=1
	return B
def encapsulation_label(relationship,entity):
	A=_A
	for B in relationship[_B]:
		if B[_C]==entity:A=B[_f];break
	if A is _A:return
	return cardinality_label(A)
def guided_parent_states(non_main,main_entities,relationships,adjacent,distances,relationship_scores,update_entity_scores,allow_loss,width):
	J=distances;E=update_entity_scores;F=[{_l:{},_m:{},_Q:[],_H:0,_D:0,_X:''}];G=0
	for A in E:
		if E[A]>G:G=E[A]
	for A in non_main:
		K=[]
		for B in F:
			L=adjacent[A][:];L.sort()
			for(C,H)in L:
				if J[H]!=J[A]-1:continue
				P=relationships[C];D=encapsulation_label(P,A)
				if D is _A:continue
				if not allow_loss and(D=='XL'or D==_p):continue
				M=B[_l].copy();N=B[_m].copy();O=B[_Q][:];M[A]=H;N[A]=C;O.append({_F:C,_C:A,_z:H});I=B[_D]
				if D=='XR'or D==_p:
					I+=1
					if G>0:I+=E.get(A,0)/G
				K.append({_l:M,_m:N,_Q:O,_H:B[_H]+relationship_scores.get(C,0),_D:I,_X:B[_X]+C+'>'+H+'|'})
		F=prune_guided_states(K,width)
		if len(F)==0:break
	return F
def reference_storage_cost(relationship_name,stored_in,relationships,data_system):
	D=data_system;C=relationships;B=stored_in;A=relationship_name;G=C.get(A)
	if G is _A:return 0
	E=D[_g][_M].get(B,{}).get(_A7)
	if E is _A:return 0
	F=relationship_average(A,B,C,D[_g][_J])
	if F is _A:return 0
	return E*F
def reference_growth_cost(relationship_name,stored_in,relationships,data_system):
	P='future_avg_connected';K=relationships;G=data_system;F=stored_in;E=relationship_name;B=relationship_average(E,F,K,G[_g][_J])
	if B is _A:return 0
	Q=G[_g][_J].get(E,{});C=_A
	for L in Q.get(_B,[]):
		if L.get(_C)==F:C=L;break
	if C is _A:return 0
	if P in C:A=C[P]
	else:
		M=C.get('growth_per_time_unit');N=G[_q].get('planning_horizon')
		if M is _A or N is _A:return 0
		A=B+N*M
	D=K.get(E)
	if D is not _A:
		H=_A
		for O in range(len(D[_B])):
			if D[_B][O][_C]==F:H=O;break
		if H is not _A:
			I=D[_B][H][_f][_b]
			if I!='N'and A>I:A=I
	J=C.get(_A0)
	if J is not _A and A>J:A=J
	if A<=B:return 0
	if B==0:return A
	return(A-B)/B
def guided_reference_options(relationship_name,relationship,main_entities,relationships,data_system):
	J=data_system;I=relationships;H=main_entities;G=relationship;C=relationship_name;A=G[_B][0][_C];B=G[_B][1][_C];D=[]
	if A==B:K=G[_B][0].get(_k);L=G[_B][1].get(_k);E={_F:C,_R:A,_P:B,_O:reference_label(B,H),_U:K,_W:L};F={_F:C,_R:B,_P:A,_O:reference_label(A,H),_U:L,_W:K};D.append({_I:[E],_H:0,_D:0,_K:0,_L:0});D.append({_I:[F],_H:0,_D:0,_K:0,_L:0});D.append({_I:[E,F],_H:0,_D:1,_K:0,_L:0});return D
	M=reference_storage_cost(C,A,I,J);N=reference_storage_cost(C,B,I,J);O=reference_growth_cost(C,A,I,J);P=reference_growth_cost(C,B,I,J);E={_F:C,_R:A,_P:B,_O:reference_label(B,H)};F={_F:C,_R:B,_P:A,_O:reference_label(A,H)};D.append({_I:[E],_H:0,_D:0,_K:M,_L:O});D.append({_I:[F],_H:0,_D:0,_K:N,_L:P});D.append({_I:[E,F],_H:0,_D:1,_K:M+N,_L:O+P});return D
def reference_storage_key(state):A=state;return A[_K],A[_D],A[_L],state_signature(A)
def reference_growth_key(state):A=state;return A[_L],A[_K],A[_D],state_signature(A)
def reference_penalty_key(state):A=state;return A[_D],A[_K],A[_L],state_signature(A)
def prune_reference_states(states,width):
	D=width;B=states
	if len(B)<=D:return B
	F=B[:];G=B[:];H=B[:];F.sort(key=reference_storage_key);G.sort(key=reference_growth_key);H.sort(key=reference_penalty_key);A=[];E=set();C=0
	while len(A)<D and C<len(B):
		add_unique_state(A,F[C],E)
		if len(A)==D:break
		add_unique_state(A,G[C],E)
		if len(A)==D:break
		add_unique_state(A,H[C],E);C+=1
	return A
def complete_query_key(state):A=state;return-A[_H],A[_D],A[_K],A[_L],state_signature(A)
def complete_storage_key(state):A=state;return A[_K],A[_L],A[_D],-A[_H],state_signature(A)
def complete_growth_key(state):A=state;return A[_L],A[_K],A[_D],-A[_H],state_signature(A)
def complete_penalty_key(state):A=state;return A[_D],A[_K],A[_L],-A[_H],state_signature(A)
def prune_complete_states(states,width):
	D=width;B=states
	if len(B)<=D:return B
	F=B[:];G=B[:];H=B[:];I=B[:];F.sort(key=complete_query_key);G.sort(key=complete_storage_key);H.sort(key=complete_growth_key);I.sort(key=complete_penalty_key);A=[];E=set();C=0
	while len(A)<D and C<len(B):
		add_unique_state(A,F[C],E)
		if len(A)==D:break
		add_unique_state(A,G[C],E)
		if len(A)==D:break
		add_unique_state(A,H[C],E)
		if len(A)==D:break
		add_unique_state(A,I[C],E);C+=1
	return A
def reference_option_key(option):
	C=':';B=''
	for A in option[_I]:
		B+=A[_F]+C+A[_R]+C+A[_P]
		if _U in A:B+=C+A[_U]
		if _W in A:B+=C+A[_W]
		B+='|'
	return B
def guided_reference_states(remaining,main_entities,relationships,parent_state,width,data_system):
	G=relationships;F=remaining;D=parent_state;C=[{_I:[],_H:D[_H],_D:D[_D],_K:0,_L:0,_X:D[_X]}];K=len(F)<=guided_reference_exact_limit
	for H in F:
		L=G[H];I=guided_reference_options(H,L,main_entities,G,data_system);I.sort(key=reference_option_key);E=[]
		for A in C:
			for B in I:
				J=A[_I][:]
				for M in B[_I]:J.append(M)
				E.append({_I:J,_H:A[_H]+B[_H],_D:A[_D]+B[_D],_K:A[_K]+B[_K],_L:A[_L]+B[_L],_X:A[_X]+reference_option_key(B)})
		if K:C=E
		else:C=prune_reference_states(E,width)
	return C
def guided_labelings_for_main_set(data_system,entities,main_entities,relationships,adjacent,relationship_scores,update_entity_scores,allow_loss,beam_width,reference_width):
	J=beam_width;I=adjacent;G=entities;F=relationships;B=main_entities;C=distances_from_main(B,I);K=[];H=0
	for E in C:
		if C[E]>H:H=C[E]
	for P in range(1,H+1):
		for E in sorted(G):
			if C[E]==P:K.append(E)
	Q=guided_parent_states(K,B,F,I,C,relationship_scores,update_entity_scores,allow_loss,J);L=[]
	for A in Q:
		R=build_labels(G,B,F,C,A[_l],A[_m]);S=build_partition(G,B,A[_l],A[_m]);M=[]
		for T in A[_Q]:M.append(T[_F])
		N=[]
		for O in sorted(F):
			if O not in M:N.append(O)
		U=guided_reference_states(N,B,F,A,reference_width,data_system)
		for D in U:L.append({_T:B[:],_V:R[:],_Q:A[_Q][:],_I:D[_I][:],_S:S,_H:D[_H],_D:D[_D],_K:D[_K],_L:D[_L],_X:D[_X]})
	return prune_complete_states(L,J)
def guided_candidate_key(candidate):
	B=candidate;A=''
	for C in B[_T]:A+=C+'|'
	A+=B.get(_X,'');return A
def generate_guided_labelings(er_schema,data_system):
	G=er_schema;C=data_system;B,I,D=schema_graph(G);J=connected_components(B,D);K,L,M,N=guided_workload_scores(G,C);H=guided_main_entity_sets(B,J,D,K,N,guided_main_pivots);O=C[_q][_A1];E=[]
	for P in H:
		Q=guided_labelings_for_main_set(C,B,P,I,D,L,M,O,guided_beam_width,guided_reference_width)
		for A in Q:E.append(A)
	E.sort(key=guided_candidate_key);F=[]
	for A in E:R={_Z:f"L{len(F)+1:06d}",_T:A[_T],_V:A[_V],_Q:A[_Q],_I:A[_I],_S:A[_S]};F.append(R)
	S={_A8:len(H),_A9:guided_beam_width,'pivots':min(guided_main_pivots,len(B))};return F,S
def document_limit(data_system):
	A=data_system[_h][_c][_N]
	if A==_i:return 16777216
	if A==_r:return 20971520
def array_size(item_size,count,technology):
	D=technology;C=item_size;A=count
	if A<0:return
	if D==_i:
		E=0;B=0;F=10;G=1
		while B<A:H=min(A,F);E+=(H-B)*G;B=H;F*=10;G+=1
		return 5+A*C+A*2+E
	if D==_r:
		if A==0:return 2
		return 2+A*C+A-1
def object_size(fields,technology):
	E=technology;B=fields
	if E==_i:
		A=5
		for(C,D)in B:A+=1+len(C.encode(_A2))+1+D
		return A
	if E==_r:
		A=2
		for F in range(len(B)):
			C,D=B[F];A+=len(C.encode(_A2))+3+D
			if F!=len(B)-1:A+=1
		return A
def attribute_size(attribute,statistics,technology):
	F='max_size_bytes';E=attribute;C=technology;B=statistics
	if B is _A or F not in B:return
	A=B[F]
	if E['type']in['string','date','time','datetime']:
		if C==_i:A+=5
		elif C==_r:A+=2
	D=E[_f][_b]
	if D=='N':return
	if D==1:return A
	return array_size(A,D,C)
def side_index(relationship,entity,role=_A):
	A=relationship
	for B in range(len(A[_B])):
		C=A[_B][B]
		if C[_C]!=entity:continue
		if role is not _A and C.get(_k)!=role:continue
		return B
def max_connected(relationship_name,entity,role,size_data):
	L='max_connected';J=size_data;I=entity;H=relationship_name;D=J[_J][H];M=J[_s].get(H,{});E=M.get(_B,[]);F=side_index(D,I,role)
	if F is _A:return
	if D[_B][0][_C]==D[_B][1][_C]:
		if len(E)==2:A=E[F]
		else:A={}
	else:
		A={}
		for B in E:
			if B.get(_C)==I:A=B;break
	if L in A:return A[L]
	C=[];K=D[_B][F][_f][_b]
	if K!='N':C.append(K)
	if _A0 in A:C.append(A[_A0])
	if len(C)==0:return
	G=C[0]
	for B in C[1:]:
		if B<G:G=B
	return G
def identifier_size(entity,size_data,technology,cache,path):
	H=technology;G=cache;D=size_data;B=path;A=entity
	if A in G:return G[A]
	if A in B:return
	B.append(A);K=D[_M][A];E=[]
	for C in K['identifier']:
		L=_E
		for M in K[_d]:
			if M[_N]!=C:continue
			Q=D[_t].get(A,{}).get(_d,{}).get(C);F=attribute_size(M,Q,H)
			if F is _A:B.pop();return
			E.append((C,F));L=_G;break
		if L:continue
		if C not in D[_J]:B.pop();return
		N=D[_J][C];I=N[_B][0][_C];O=N[_B][1][_C]
		if I==O:B.pop();return
		if I==A:P=O
		else:P=I
		F=identifier_size(P,D,H,G,B)
		if F is _A:B.pop();return
		E.append((C,F))
	B.pop()
	if len(E)==1:J=E[0][1]
	else:J=object_size(E,H)
	G[A]=J;return J
def prepare_size_data(er_schema,data_system):
	C=data_system;B=er_schema;A={_M:{},_J:{},_t:C.get(_g,{}).get(_M,{}),_s:C.get(_g,{}).get(_J,{})}
	for D in B[_M]:A[_M][D[_N]]=D
	for E in B[_J]:A[_J][E[_N]]=E
	return A
def entity_max_size(entity,main_entities,children,references,size_data,technology,identifier_cache,entity_cache):
	e='_id';V=identifier_cache;U=references;T=children;N=entity_cache;J=main_entities;D=size_data;B=entity;A=technology
	if B in N:return N[B]
	f=D[_M][B];I=[]
	if B in J and A==_i:I.append((e,12))
	for C in f[_d]:
		K=D[_t].get(B,{}).get(_d,{}).get(C[_N]);E=attribute_size(C,K,A)
		if E is _A:return
		I.append((C[_N],E))
	for W in T.get(B,[]):
		F=W[_F];X=W[_C];H=D[_J][F];G=max_connected(F,B,_A,D)
		if G is _A:return
		Q=entity_max_size(X,J,T,U,D,A,V,N)
		if Q is _A:return
		L=side_index(H,B)
		if L is _A:return
		if H[_B][L][_f][_b]==1:Y=Q
		else:Y=array_size(Q,G,A)
		Z=[(X,Y)];R=D[_s].get(F,{}).get(_d,{})
		for C in H.get(_d,[]):
			K=R.get(C[_N]);E=attribute_size(C,K,A)
			if E is _A:return
			if G>1:E=array_size(E,G,A)
			Z.append((C[_N],E))
		I.append((F,object_size(Z,A)))
	for S in U.get(B,[]):
		F=S[_F];M=S[_P];a=S.get(_U);G=max_connected(F,B,a,D)
		if G is _A:return
		if M in J and A==_i:O=12
		else:O=identifier_size(M,D,A,V,[])
		if O is _A:return
		H=D[_J][F];L=side_index(H,B,a)
		if L is _A:return
		b=H[_B][L][_f][_b]!=1
		if b:E=array_size(O,G,A);c='_ids'if M in J else'_keys'
		else:E=O;c=e if M in J else'_key'
		I.append((M+c,E));R=D[_s].get(F,{}).get(_d,{})
		for C in H.get(_d,[]):
			K=R.get(C[_N]);P=attribute_size(C,K,A)
			if P is _A:return
			if b:P=array_size(P,G,A)
			I.append((F+'_'+C[_N],P))
	d=object_size(I,A);N[B]=d;return d
def candidate_document_sizes(labeling,size_data,data_system):
	G=data_system;B=size_data;A=labeling;N=G[_h][_c][_N];C=document_limit(G)
	if C is _A:return
	D={};E={}
	for H in B[_M]:D[H]=[];E[H]=[]
	for I in A[_Q]:D[I[_z]].append(I)
	for J in A[_I]:E[J[_R]].append(J)
	O={};P={};K=[]
	for L in A[_S]:
		M=L[_y];F=entity_max_size(M,A[_T],D,E,B,N,O,P)
		if F is _A:return
		Q=B[_t].get(M,{}).get(_A7);K.append({_j:L[_j],'document_count':Q,'max_document_bytes':F,'document_limit_bytes':C,_u:1-F/C})
	return K
def has_information_loss(labeling):
	for A in labeling[_V]:
		if A[_O]=='XL'or A[_O]==_p:return _G
	return _E
def filter_labelings(er_schema,data_system,labelings):
	B=data_system;I=prepare_size_data(er_schema,B);J=B[_q][_A1];D=[];E=0;F=0;G=0
	for A in labelings:
		if not J and has_information_loss(A):E+=1;continue
		C=candidate_document_sizes(A,I,B)
		if C is _A:G+=1;continue
		H=_E
		for K in C:
			if K[_u]<0:H=_G;break
		if H:F+=1;continue
		A[_A3]={_A4:C};D.append(A)
	L={_AA:E,_AB:F,_AC:G};return D,L
def is_labeled_input(data):
	A=data
	if not isinstance(A,dict):return _E
	if _a in A or _v in A or _S in A or _n in A:return _G
	return _E
def input_labeling(labeled_schema):
	A=labeled_schema;D={_w:A.get(_w,'1.0'),_M:A[_v][_M],_J:A[_v][_J]};C=[]
	for E in A[_a][_T]:C.append(E[_C])
	B=A.get(_n)
	if B is _A:B='INPUT'
	F={_Z:B,_T:C,_V:A[_a][_V],_Q:A[_a][_Q],_I:A[_a][_I],_S:A[_S]};return D,F
def prepare_input_labeling(er_schema,data_system,labeling):
	B=labeling;A=data_system
	if not A[_q][_A1]and has_information_loss(B):return'Lo schema etichettato non è ammissibile perché può comportare perdita di informazione.'
	D=prepare_size_data(er_schema,A);C=candidate_document_sizes(B,D,A)
	if C is _A:return
	for E in C:
		if E[_u]<0:return'Lo schema etichettato non è ammissibile perché può superare la dimensione massima dei documenti.'
	B[_A3]={_A4:C}
def evaluate_labelings(er_schema,data_system,labelings,selected_metrics):
	F=selected_metrics;E=data_system;D=er_schema;G=[];C={1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0,13:0,14:0,15:0,16:0,17:0}
	for B in labelings:
		A={}
		if 1 in F:
			A[1]=tc_norm(D,E,B)
			if A[1]is _A:C[1]+=1
		if 2 in F:
			A[2]=tc_w(D,E,B)
			if A[2]is _A:C[2]+=1
		if 3 in F:
			A[3]=documents_ratio(D,E,B)
			if A[3]is _A:C[3]+=1
		if 4 in F:
			A[4]=volume_ratio(D,E,B)
			if A[4]is _A:C[4]+=1
		if 5 in F:
			A[5]=intermediate_results(D,E,B)
			if A[5]is _A:C[5]+=1
		if 6 in F:
			A[6]=working_set(D,E,B)
			if A[6]is _A:C[6]+=1
		if 7 in F:
			A[7]=index_memory(D,E,B)
			if A[7]is _A:C[7]+=1
		if 8 in F:
			A[8]=temporary_storage(D,E,B)
			if A[8]is _A:C[8]+=1
		if 9 in F:
			A[9]=document_margin(D,E,B)
			if A[9]is _A:C[9]+=1
		if 10 in F:
			A[10]=document_growth(D,E,B)
			if A[10]is _A:C[10]+=1
		if 11 in F:
			A[11]=network_volume(D,E,B)
			if A[11]is _A:C[11]+=1
		if 12 in F:
			A[12]=storage_space(D,E,B)
			if A[12]is _A:C[12]+=1
		if 13 in F:
			A[13]=tw_norm(D,E,B)
			if A[13]is _A:C[13]+=1
		if 14 in F:
			A[14]=update_documents(D,E,B)
			if A[14]is _A:C[14]+=1
		if 15 in F:
			A[15]=rewrite_ratio(D,E,B)
			if A[15]is _A:C[15]+=1
		if 16 in F:
			A[16]=multi_document_updates(D,E,B)
			if A[16]is _A:C[16]+=1
		if 17 in F:
			A[17]=lifecycle_volume(D,E,B)
			if A[17]is _A:C[17]+=1
		G.append({_Z:B[_Z],_a:B,_e:A})
	return G,C
def evaluable_results(results,selected_metrics):
	A=[]
	for B in results:
		C=_G
		for D in selected_metrics:
			if B[_e].get(D)is _A:C=_E;break
		if C:A.append(B)
	return A
def dominates(first,second,selected_metrics):
	D=_E
	for A in selected_metrics:
		B=first[_e][A];C=second[_e][A]
		if A==9 or A==13:
			if B<C:return _E
			if B>C:D=_G
		else:
			if B>C:return _E
			if B<C:D=_G
	return D
def pareto_front(results,selected_metrics):
	E=selected_metrics;A=[]
	for C in results:
		F=_E
		for B in A:
			if dominates(B,C,E):F=_G;break
		if F:continue
		D=[]
		for B in A:
			if not dominates(C,B,E):D.append(B)
		D.append(C);A=D
	return A
def metric_limits(front,selected_metrics):
	E=front;F={}
	for B in selected_metrics:
		A=E[0][_e][B];C=A
		for I in E[1:]:
			D=I[_e][B]
			if D<A:A=D
			if D>C:C=D
		if B==9 or B==13:G=C;H=A
		else:G=A;H=C
		F[B]={_o:A,_b:C,'ideal':G,'nadir':H}
	return F
def normalized_deviation(value,metric,limits):
	E=limits;D=value;B=metric;A=E[B]['ideal'];C=E[B]['nadir']
	if A==C:return 0
	if B==9 or B==13:return(A-D)/(A-C)
	return(D-A)/(C-A)
def chebyshev_values(result,selected_metrics,limits):
	D=selected_metrics;E=[];B=0;F=0
	for C in D:
		G=result[_e][C];A=normalized_deviation(G,C,limits);E.append({'metric':C,'value':A})
		if A>B:B=A
		F+=A
	H=F/len(D);return B,H,E
def choose_recommended(front,selected_metrics):
	J=selected_metrics;I=front;K=metric_limits(I,J);D=_A;E=_A;B=[];F=1e-12
	for A in I:
		G,C,L=chebyshev_values(A,J,K);A['selection']={'chebyshev':G,'average_deviation':C,'normalized_deviations':L}
		if D is _A or G<D-F:D=G;E=C;B=[A];continue
		if abs(G-D)<=F:
			if C<E-F:E=C;B=[A]
			elif abs(C-E)<=F:B.append(A)
	H=B[0]
	for A in B[1:]:
		if A[_Z]<H[_Z]:H=A
	return H,B,K
def select_labeling(results,selected_metrics):
	F='limits';E='equivalent';D='pareto';A=selected_metrics;B=evaluable_results(results,A)
	if len(B)==0:return{_A5:[],D:[],_x:_A,E:[],F:{}}
	C=pareto_front(B,A);G,H,I=choose_recommended(C,A);return{_A5:B,D:C,_x:G,E:H,F:I}
metric_names=['TC_norm','TC_w','documents_ratio','volume_ratio','intermediate_results','working_set','index_memory','temporary_storage',_u,'document_growth','network_volume','storage_space','TW_norm','update_documents','rewrite_ratio','multi_document_updates','lifecycle_volume'];metric_units=[_Y,_Y,'documents/result',_Y,'elements/query',_Y,_Y,_Y,_Y,_Y,'bytes/query','bytes',_Y,'documents/update',_Y,_Y,'bytes']
def calculate_metric(metric,er_schema,data_system,labeling):
	D=labeling;C=data_system;B=er_schema;A=metric
	if A==1:return tc_norm(B,C,D)
	if A==2:return tc_w(B,C,D)
	if A==3:return documents_ratio(B,C,D)
	if A==4:return volume_ratio(B,C,D)
	if A==5:return intermediate_results(B,C,D)
	if A==6:return working_set(B,C,D)
	if A==7:return index_memory(B,C,D)
	if A==8:return temporary_storage(B,C,D)
	if A==9:return document_margin(B,C,D)
	if A==10:return document_growth(B,C,D)
	if A==11:return network_volume(B,C,D)
	if A==12:return storage_space(B,C,D)
	if A==13:return tw_norm(B,C,D)
	if A==14:return update_documents(B,C,D)
	if A==15:return rewrite_ratio(B,C,D)
	if A==16:return multi_document_updates(B,C,D)
	if A==17:return lifecycle_volume(B,C,D)
def metric_output(metric,value):A=metric;return{_Z:A,_N:metric_names[A-1],'value':value,'unit':metric_units[A-1]}
def remaining_metrics(er_schema,data_system,recommended,selected_metrics):
	D=data_system;C=er_schema;E=[];B=[];G=recommended[_a]
	for A in range(1,18):
		if A in selected_metrics:continue
		H=check_metric_data(C,D,[A])
		if H:B.append(A);continue
		F=calculate_metric(A,C,D,G)
		if F is _A:B.append(A);continue
		E.append(metric_output(A,F))
	return E,B
def evaluate_input_labeling(er_schema,data_system,labeling,selected_metrics):
	D=data_system;C=er_schema;E=[];B=[]
	for A in selected_metrics:
		G=check_metric_data(C,D,[A])
		if G:B.append(A);continue
		F=calculate_metric(A,C,D,labeling)
		if F is _A:B.append(A);continue
		E.append(metric_output(A,F))
	return E,B
def output_labeling(labeling):
	B=labeling;E=[]
	for C in B[_T]:
		F=C
		for G in B[_S]:
			if G[_y]==C:F=G[_j];break
		E.append({_C:C,_j:F})
	H=[]
	for A in B[_I]:
		D={_F:A[_F],_R:A[_R],_P:A[_P],_O:A[_O]}
		if _U in A:D[_U]=A[_U]
		if _W in A:D[_W]=A[_W]
		H.append(D)
	return{_T:E,_V:B[_V],_Q:B[_Q],_I:H}
def write_json(path,data):
	try:
		with open(path,'w',encoding=_A2)as A:json.dump(data,A,ensure_ascii=_E,indent=2);A.write('\n')
	except OSError as B:return str(B)
def write_output(er_schema,data_system,results,selected_metrics):
	G=selected_metrics;F=data_system;B=er_schema;C=results[_x];H=C[_a];I=[]
	for J in G:I.append(metric_output(J,C[_e][J]))
	M,D=remaining_metrics(B,F,C,G);N={'optimized_metrics':I,'remaining_metrics':M};O={_w:B.get(_w,'1.0'),_n:C[_Z],_c:F[_h][_c],_v:{_M:B[_M],_J:B[_J]},_a:output_labeling(H),_S:H[_S]};E='output'
	try:os.makedirs(E,exist_ok=_G)
	except OSError as A:return _A,_A,D,str(A)
	K=os.path.join(E,_AD);L=os.path.join(E,'labeled_schema.json');A=write_json(K,N)
	if A is not _A:return _A,_A,D,A
	A=write_json(L,O)
	if A is not _A:return _A,_A,D,A
	return K,L,D,_A
def write_input_evaluation(labeled_schema,data_system,evaluated):
	A={};C=labeled_schema.get(_n)
	if C is not _A:A[_n]=C
	A[_c]=data_system[_h][_c];A['evaluated_metrics']=evaluated;D='output'
	try:os.makedirs(D,exist_ok=_G)
	except OSError as B:return _A,str(B)
	E=os.path.join(D,_AD);B=write_json(E,A)
	if B is not _A:return _A,B
	return E,_A
def print_input_summary(er_schema,data_system):B=er_schema;A=data_system;print(f"Entità: {len(B[_M])}");print(f"Relazioni: {len(B[_J])}");print(f"Query: {len(A[_A6]["queries"])}");print(f"Tecnologia: {A[_h][_c][_N]} {A[_h][_c]["version"]}")
def run_labeling_generation(er_schema,data_system):
	D=data_system;B=er_schema;C=choose_metrics();K=check_metric_data(B,D,C)
	if K:
		print('\nDati insufficienti per le metriche selezionate:')
		for F in K:print(f"- {F}")
		return
	print('\nMetriche selezionate:')
	for A in C:print(f"{A:2}. {metrics[A-1]}")
	print('\nControllo degli input completato.')
	if len(B[_M])<=exact_entity_limit:G=generate_labelings(B)
	else:G,L=generate_guided_labelings(B,D);print(f"Ricerca guidata: {L[_A8]} insiemi di main entity, beam width {L[_A9]}.");print("La ricerca guidata limita lo spazio esplorato: l'ottimo globale non è garantito.")
	print(f"Etichettature complete generate: {len(G)}");H,I=filter_labelings(B,D,G);print(f"Scartate per perdita di informazione: {I[_AA]}");print(f"Scartate per dimensione dei documenti: {I[_AB]}");print(f"Non verificabili per dimensione dei documenti: {I[_AC]}");print(f"Etichettature ammissibili: {len(H)}")
	if len(H)==0:print('Nessuna etichettatura ammissibile con i dati forniti.');return
	O,M=evaluate_labelings(B,D,H,C);E=[]
	for A in C:E.append(str(A))
	print('Metriche calcolate: '+', '.join(E))
	for A in C:
		if M[A]>0:print(f"Metrica {A} non calcolabile per {M[A]} etichettature.")
	J=select_labeling(O,C);print(f"Etichettature valutabili sulle 5 metriche: {len(J[_A5])}")
	if J[_x]is _A:print('Nessuna etichettatura è valutabile su tutte le metriche selezionate.');return
	P,Q,N,F=write_output(B,D,J,C)
	if F is not _A:print(f"Errore durante la scrittura dei file di output: {F}");return
	if N:
		E=[]
		for A in N:E.append(str(A))
		print('Metriche rimanenti non calcolabili: '+', '.join(E))
	print('File di output scritti:');print(f"- {P}");print(f"- {Q}")
def run_labeled_evaluation(labeled_schema,er_schema,data_system,labeling):
	E=labeling;D=er_schema;C=data_system;A=prepare_input_labeling(D,C,E)
	if A is not _A:print(A);return
	if E.get(_A3,{}).get(_A4)is _A:print('Dimensione massima dei documenti non verificabile con i dati forniti.')
	G=choose_evaluation_metrics();print('\nMetriche selezionate per la valutazione:')
	for B in G:print(f"{B:2}. {metrics[B-1]}")
	H,F=evaluate_input_labeling(D,C,E,G)
	if len(H)==0:
		print('Nessuna delle metriche selezionate è calcolabile con i dati forniti.')
		for B in F:
			J=check_metric_data(D,C,[B])
			for A in J:print(f"- {A}")
		return
	if F:
		I=[]
		for B in F:I.append(str(B))
		print('Metriche non calcolabili: '+', '.join(I))
	K,A=write_input_evaluation(labeled_schema,C,H)
	if A is not _A:print(f"Errore durante la scrittura del file di output: {A}");return
	print('File di output scritto:');print(f"- {K}")
def main():
	I='\nErrori in data_system.json:'
	if len(sys.argv)!=3:print('Uso: python3 main_clean_obf_1_4.py <er_schema.json|labeled_schema.json> <data_system.json>');return
	D,A=read_json(sys.argv[1])
	if A is not _A:print(A);return
	C,A=read_json(sys.argv[2])
	if A is not _A:print(A);return
	if is_labeled_input(D):
		F=check_labeled_schema(D)
		if F:
			print('\nErrori in labeled_schema.json:')
			for A in F:print(f"- {A}")
			return
		B,J=input_labeling(D);E=check_data_system(C,B)
		if E:
			print(I)
			for A in E:print(f"- {A}")
			return
		G=check_labeled_technology(D,C)
		if G:
			print('\nInput incoerenti:')
			for A in G:print(f"- {A}")
			return
		print('\nSchema etichettato e file di sistema validi.');print_input_summary(B,C);run_labeled_evaluation(D,B,C,J);return
	B=D;H=check_er_schema(B)
	if H:
		print('\nErrori in er_schema.json:')
		for A in H:print(f"- {A}")
		return
	E=check_data_system(C,B)
	if E:
		print(I)
		for A in E:print(f"- {A}")
		return
	print('\nFile di input validi.');print_input_summary(B,C);run_labeling_generation(B,C)
if __name__=='__main__':main()
