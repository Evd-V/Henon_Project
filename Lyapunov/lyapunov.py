import numpy as np

import general as ge
from full_attractor import Henon

def norm_vect(vector):
    """ Calculate the norm of a vector. """
    values = [i*i for i in vector]
    return sum(values)

def inner_vect(vect1, vect2):
    """ Calculate the inner product of two vectors. """
    values = [vect1[i] * vect2[i] for i in range(len(vect1))]
    return sum(values)

def proj_vect(vect1, vect2):
    """ Calculate the projection of vector v onto vector u. """
    return (inner_vect(vect1, vect2) / norm_vect(vect1)) * vect1

def basis(dim):
    """ Creating the standard basis vectors for n dimensions. """
    
    basisVects = [np.zeros(dim) for i in range(dim)]    
    for i in range(dim):
        basisVects[i][i] += 1
    
    return basisVects
    
def Gram_Schmidt(vectors):
    """ Function that uses the Gram-Schmidt process to orthogonalize a set of n-dimensional 
        vectors. The normalization of the vectors is not included.
        
        Input: vectors = list containing the vectors; a valid input is for example:
                         [v1, v2] where v1 = [[x1], [y1]] and v2 = [[x2], [y2]];
                         
        Returns: basis = list containing the orthogonalised set of vectors in the same format 
                         as the input 'vectors'.
    """
    basis = [vectors[0]]
    for v in range(1, len(vectors)):
        for j in range(v):
            new_vect = vectors[v] - proj_vect(vectors[j], vectors[v])
        basis.append(new_vect)
            
    return basis

def Lyapunov(N, basis, xvalues, A, B):
    """ Function that calculates the Lyapunov exponents for the Henon map.
        For now this function only works for the Hénon map, still working on making it more general.
    
    
        Input:      N       = number of loops that have to be computed (integer);
                    basis   = the standard basis vectors in n dimensions. The syntax is for example: 
                              [e1, e2] where e1 = [[1], [0]] and e2 = [[0], [1]] (list);
                    xvalues = list of x values of the Hénon map;
                    A       = value for parameter a for the Hénon map;
                    B       = value for parameter b for the Hénon map;
                    
        Returns:    lya     = list containing the computed lyapunov exponents.
    """
    
    dim = len(basis)                          # Dimension
    exponents = [0 for i in range(dim)]       # Array to put the intermediate results in
    
    # First step
    J = np.array([[-2*A*xvalues[0], 1], [B, 0]])            # The 'first' Jacobian
    v_1k = [np.matmul(J, b) for b in basis]                 # Calculating the 'first' v_nk
    u_nk = Gram_Schmidt([v_1k[i] for i in range(dim)])      # Calculating the 'first' u_nk
    
    # Adding to 'exponents', used for the calculating of the Lyapunov exponents
    for i in range(dim):
        u_i = u_nk[i]
        norm_v = norm_vect(u_i)                             # Norm of the vector
        exponents[i] += np.log(norm_v)                      # Adding the newly obtained value to the array 'exponents'
        u_nk[i] = u_i / norm_v                              # Normalizing
    
    for n in range(1, N):
        
        v_nk = [np.matmul(J, u) for u in u_nk]              # Calculating v_nk
        u_nk = Gram_Schmidt([v_nk[i] for i in range(dim)])  # Gram-Schmidt
        
        for i in range(dim):
            u_i = u_nk[i]
            norm_v = norm_vect(u_i)                       # Norm of the vector
            exponents[i] += np.log(norm_v)                # Adding the newly obtained value to the array 'exponents'
            u_nk[i] = u_i / norm_v                        # Normalizing
        
        J = np.array([[-2*A*xvalues[n], 1], [B, 0]])      # Updating the Jacobian matrix
        
    # Calculating the lyapunov exponents
    lya = [exponents[i] / N for i in range(dim)]
    
    return lya

def lyapunov_point(xp, av, bv):
    """ Function that calculates the Lyapunov exponents for a point attractor of the Hénon 
        map. For point attractors it can be shown that the Lyapunov numbers are equal to 
        the eigenvalues of the Jacobian matrix at the attracting point. The Lyapunov exponents 
        can then be calculated by taking the natural logarithm of the Lyapunov numbers. This 
        calculation is a lot quicker than the general way of calculating Lyapunov exponents. 
        In this function the eigenvalues are found by solving the characteristic equation.
        
        Input:      xp = x coordinate of attracting point (float);
                    av = a value of the Hénon map (float);
                    bv = b value of the Hénon map (float);
                    
        Returns:    sorted list containing both Lyapunov exponents (list).
    """
    
    # Finding the eigenvalues at the given point
    sol1, sol2 = ge.solve_eig_vals(xp, av, bv)
    
    # Finding the Lyapunov exponents
    lya1 = np.log(abs(sol1))
    lya2 = np.log(abs(sol2))
    
    return [max(lya1, lya2), min(lya1, lya2)]

def lyapunov_period(xpoints, av, bv):
    """ Function that finds the Lyapunonv exponents of a periodic set of points for the Hénon 
        map. This is done by first taking finding the eigenvalues at each periodic point using 
        the same method as for a point attractor. Subsequently all these exponents are taken 
        together and the average of these is found.
        
        Input:      xpoints = the x coordinates that are periodic (list);
                    av   = the a parameter of the Hénon map (float);
                    bv   = the b parameter of the Hénon map (float);
                    
        Returns:    list containing the maximum and minimum Lyapunov exponents respectively (list).
    """
    # Creating empty lists to put the exponents in
    lya1, lya2 = [], []
    
    # Looping over all periodic points
    for x in xpoints:
        # Finding the exponents for each point
        lya_max, lya_min = lyapunov_point(x, av, bv)
        
        # Adding the exponents to the lists
        lya1.append(lya_max)
        lya2.append(lya_min)
        
    return [max(np.mean(lya1), np.mean(lya2)), min(np.mean(lya1), np.mean(lya2))]

def calc_lya_henon(Ninit, cutoff, start, A, B, div=True, thres=1e5):
    """ Calculation of the Lyapunov exponents specifically for the Hénon map.
        If using arrays for A and B to for example create a Lyapunov grid, it can get 
        really slow. Especially for a large number of different A and B values as it 
        has to calculate Ninit points for the Hénon map and subsequently calculate the 
        Lyapunov exponents. One can imagine that even for a 10x10 grid of A and B values 
        this can quickly increase significantly in computation time. Therefore an option 
        is to reduce Ninit which in turn decreases the accuracy of the Lyapunov 
        exponents. However, for the creation of a Lyapunov grid these values do not 
        have to be super exact but rather in the right ball park.
    
        Input:      Ninit   = number of iterations for the Hénon map (integer);
                    Cutoff  = number of points that get thrown away (integer);
                    start   = intial starting point for the Hénon map (tuple);
                    A       = value of the 'a' parameter in the iterative equations (float);
                    B       = value of the 'b' parameter in the iterative equations (float);
                
        Returns:    lya     = the Lyapunov exponents for the Hénon map (list).
    """
    
    # First checking if A and B are arrays
    if isinstance(A, np.ndarray) and isinstance(B, np.ndarray):
        
        basisVects = basis(len(start))          # Basis vectors
        all_exp1, all_exp2 = [], []             # List to put exponents in
        
        # Looping over all values of the 'a' parameter
        for a in A:
            a_exp1, a_exp2 = [], []
            
            # Improvement in computing speed
            exp1_add = a_exp1.append
            exp2_add = a_exp2.append
            
            # Looping over all values of the 'b' parameter
            for b in B:
                
                # Generating the points of the Hénon map
                xvalues, yvalues = Henon(start[0], start[1], Ninit, a, b, div=div)
                
                # First checking if the Hénon map diverges
                if xvalues == None:
                    exp1_add(None)
                    exp2_add(None)
                    continue
                    
                else:
                    # Checking if we have a point attractor or a limit cycle
                    point_attr = ge.determine_point(xvalues, yvalues)
                    lim_cycle = ge.determine_period(xvalues, yvalues)
                    
                    # If we have a point attractor or limit cycle we can calculate the exponents quickly
                    if point_attr != None:
                        exp1_add(lyapunov_point(point_attr[0], a, b)[0])
                        exp2_add(lyapunov_point(point_attr[0], a, b)[1])
                        
                    elif lim_cycle != None:
                        exp1_add(lyapunov_period(lim_cycle[1], a, b)[0])
                        exp2_add(lyapunov_period(lim_cycle[1], a, b)[1])
                    
                    else:
                        # Calculating the Lyapunov exponents for all other cases
                        lya = Lyapunov(Ninit-cutoff, np.array(basisVects), xvalues[cutoff:], a, b)
                        if lya[0] != None:
                            exp1_add(max(lya))
                            exp2_add(min(lya))
                        else:
                            exp1_add(None)
                            exp2_add(None)
                
            all_exp1.append(a_exp1)
            all_exp2.append(a_exp2)
    
        return all_exp1, all_exp2
        
    # Checking if only A is an array
    elif isinstance(A, np.ndarray) and (isinstance(B, float) or isinstance(B, int)):
        all_exp1, all_exp2 = [], []
        
        # Improvement in computing speed
        exp1_add = all_exp1.append
        exp2_add = all_exp2.append
        
        # Looping over all values of the 'a' parameter
        for a in A:
            # Calculating the points of the Hénon map
            xvalues, yvalues = Henon(start[0], start[1], Ninit, a, B, div=div)
            
            # Checking if the points diverge
            if xvalues == None:
                exp1_add(None)
                exp2_add(None)
                continue
            
            else:
                # Checking if we have a point attractor or a limit cycle
                point_attr = ge.determine_point(xvalues, yvalues)
                lim_cycle = ge.determine_period(xvalues, yvalues)
                
                # If we have a point attractor or limit cycle we can calculate the exponents quickly
                if point_attr != None:
                    exp1_add(lyapunov_point(point_attr[0], a, B)[0])
                    exp2_add(lyapunov_point(point_attr[0], a, B)[1])
                    
                elif lim_cycle != None:
                    exp1_add(lyapunov_period(lim_cycle[1], a, B)[0])
                    exp2_add(lyapunov_period(lim_cycle[1], a, B)[1])
                    
                else:
                    # Calculating the Lyapunov exponents for all other cases
                    lya = Lyapunov(Ninit-cutoff, np.array(basisVects), xvalues[cutoff:], a, B)
                    if lya[0] != None:
                        exp1_add(max(lya))
                        exp2_add(min(lya))
                    else:
                        exp1_add(None)
                        exp2_add(None)
            
        return all_exp1, all_exp2
            
    # Checking if only B is an array
    elif isinstance(B, np.ndarray) and (isinstance(A, float) or isinstance(A, int)):
        all_exp1, all_exp2 = [], []
        
        # Improvement in computing speed
        exp1_add = all_exp1.append
        exp2_add = all_exp2.append
        
        # Looping over all values of the 'b' parameter
        for b in B:
            # Calculating the points of the Hénon map
            xvalues, yvalues = Henon(start[0], start[1], Ninit, A, b, div=div)
            
            # Checking if the points diverge
            if xvalues == None:
                exp1_add(None)
                exp2_add(None)
                continue
            
            else:
                # Checking if we have a point attractor or a limit cycle
                point_attr = ge.determine_point(xvalues, yvalues)
                lim_cycle = ge.determine_period(xvalues, yvalues)
                
                # If we have a point attractor or limit cycle we can calculate the exponents quickly
                if point_attr != None:
                    exp1_add(lyapunov_point(point_attr[0], A, b)[0])
                    exp2_add(lyapunov_point(point_attr[0], A, b)[1])
                    
                elif lim_cycle != None:
                    exp1_add(lyapunov_period(lim_cycle[1], A, b)[0])
                    exp2_add(lyapunov_period(lim_cycle[1], A, b)[1])
                    
                else:
                    # Calculating the Lyapunov exponents for all other cases
                    lya = Lyapunov(Ninit-cutoff, np.array(basisVects), xvalues[cutoff:], A, b)
                    if lya[0] != None:
                        exp1_add(max(lya))
                        exp2_add(min(lya))
                    else:
                        exp1_add(None)
                        exp2_add(None)
            
        return all_exp1, all_exp2
    
    # Checking if A and B are floats or integers
    elif (isinstance(A, float) or isinstance(A, int)) and (isinstance(B, float) or isinstance(B, int)):
        
        # Generating the points of the Hénon map
        xvalues, yvalues = Henon(start[0], start[1], Ninit, A, B, div=div)
        
        # Basis vectors
        basisVects = basis(len(start))
        
        # Checking if we have a point attractor or limit cycle
        point_attr = ge.determine_point(xvalues, yvalues)
        lim_cycle = ge.determine_period(xvalues, yvalues)
        
        # Checking if the values diverge
        if xvalues == None:
            return None
        
         # If we have a point attractor or limit cycle we can calculate the exponents quickly
        elif point_attr != None:
            return lyapunov_point(point_attr[0], A, B)
        
        elif lim_cycle != None:
            return lyapunov_period(lim_cycle[1], A, B)

        # For all other cases
        else:
            # Calculating the Lyapunov exponents
            lya = Lyapunov(Ninit-cutoff, np.array(basisVects), xvalues[cutoff:], A, B)

            return lya
    
    # Invalid input for A and/or B
    else:
        raise ValueError('invalid input for A and/or B parameter')
    
def create_lya_grid(a_vals, b_vals, start=(0,0), N=int(1e4), cutoff=int(1e3), div=True):
    """ Function that calculates the grid for a given arrays of a and b values. """
    vals = np.array(calc_lya_henon(N, cutoff, start, a_vals, b_vals, div=div))
    return vals[0], vals[1]

def det_att(lya1, lya2, acc=0.1):
    """ Function that finds the type of attractor for two given Lyapunov exponents; 
        it is assumed that lya1 >= lya2. For some type of attractor it is required to 
        see if either one of the two exponents are zero or that the exponents are equal 
        to each other. Since the accuracy of the exponents is limited there has to be 
        some threshold at which it is determined that an exponent is zero or that both 
        are equal to each other. The input parameter acc represents this accuracy; the 
        default value is 0.1 which is relatively high. The function returns an integer 
        between 0 and 5 which represent which type of attractor it is.
        
        Input:      lya1 = first Lyapunov exponent (float);
                    lya2 = second Lyapunov exponent (float);
                    acc = accuracy (float);
                    
        Returns:    type of attractor (integer).
    """
    
    if lya1 is None: return 5                     # No attractor
    
    # 6 possibilities, see Garst, S., & Sterk, A. E. (2018)
    elif lya1 < 0-acc:
        if lya1 > lya2+acc: return 0              # 0 > lya1 > lya2, Point attractor
        else: return 1                            # 0 > lya1 = lya2, Point attractor
        
    elif lya1 > -acc and lya1 < acc: return 2     # 0 = lya1 > lya2, Invariant circle
    elif lya1 > 0:
        if lya2 < acc: return 3                   # lya1 > 0 >= lya2, Chaotic attractor
        else: return 4                            # lya1 >= lya2 > 0, Chaotic attractor
        
    else: return 5                                # No attractor