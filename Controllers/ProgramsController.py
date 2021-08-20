from django.template.response import TemplateResponse
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from math import exp
import numpy as np
import Controllers.CommonModules.constants as const

def index (request):

    Ex = [0]
    Hy = [0]
    x_axis = [0]
    ke = "Insert value"
    t0 = "Insert value"
    spread = "Insert value"
    nsteps = "Insert value"

    #select which program to run
    request.session['Program'] =  'Program 1.1'

    if \
    'Ex' in request.session and\
    'Hy' in request.session and\
    'x_axis' in request.session and\
    'ke' in request.session and\
    't0' in request.session and\
    'spread' in request.session and\
    'nsteps' in request.session:
        Ex = request.session['Ex']
        Hy = request.session['Hy']
        x_axis = request.session['x_axis']
        ke = request.session['ke']
        t0 = request.session['t0']
        spread = request.session['spread']
        nsteps = request.session['nsteps']

    context = {
        'Ex': Ex,
        'Hy': Hy,
        'x_axis': x_axis,
        'ke': ke,
        't0': t0,
        'spread': spread,
        'nsteps': nsteps,
        'ProgramSession': request.session['Program']
    }

    return render(request, 'Programs.html', context)

def ProblemForm(request):

    ke = request.POST.get('Ke')
    t0 = request.POST.get('T0')
    spread = request.POST.get('Spread')
    nsteps = request.POST.get('nsteps')

    #inputs ke, t0, spread, nsteps
    #avoid null or empty declaration for any of the inputs

    if ke=="" or ke==None or ke=="Insert value":\
    ke = const.ke_default
    else: ke = int(request.POST.get('Ke'))

    if t0=="" or t0==None or t0=="Insert value":\
    t0 = const.t0_default
    else: t0 = int(request.POST.get('T0'))

    if spread=="" or spread==None or spread=="Insert value":\
    spread = const.spread_default
    else: spread = int(request.POST.get('Spread'))

    if nsteps=="" or nsteps==None or nsteps=="Insert value":\
    nsteps = const.nsteps_default
    else: nsteps = int(request.POST.get('nsteps'))

    SolverSession = Solver('Program 1.1',
        'numpy',
        'gauss',
        ke,
        t0,
        spread,
        nsteps)

    #session variables for current plot
    #x axis that will be ploted
    request.session['x_axis'] =  SolverSession.x_axis
    request.session['Ex'] = SolverSession.ex_list
    request.session['Hy'] = SolverSession.hy_list
    request.session['ke'] = SolverSession.ke
    request.session['t0'] = SolverSession.t0
    request.session['spread'] = SolverSession.spread
    request.session['nsteps'] = SolverSession.nsteps

    return HttpResponseRedirect('/Programs')

class Solver:

    def __init__(self,
        program,
        array_operator_type,
        source_type,
        ke,
        t0,
        spread,
        nsteps):
        self.program = program
        self.array_operator_type = array_operator_type
        self.source_type = source_type

        #Input Variables
        self.ke = ke
        self.t0 = t0
        self.spread = spread
        self.nsteps = nsteps

        #calculated values
        self.ex = np.zeros(self.ke)
        self.hy = np.zeros(self.ke)
        self.kc = int(self.ke / 2)
        self.x_axis = [] #x axis
        self.ex_list = [] #python session doesn't accept arrays
        self.hy_list = [] #python session doesn't accept arrays

        # Creating x axis (position)
        for k in range(1, self.ke + 1):
            self.x_axis.append(k)

        # Main FDTD Loop
        for time_step in range(1, self.nsteps + 1):

            # Calculate the Ex field
            for k in range(1, ke):
                self.ex[k] = self.ex[k] + 0.5 * (self.hy[k - 1] - self.hy[k])

            # Put a source pulse in the middle
            self.ex[self.kc] = self.pulse_calculator(self.source_type, time_step)

            # Calculate the Hy field
            for k in range(self.ke - 1):
                self.hy[k] = self.hy[k] + 0.5 * (self.ex[k] - self.ex[k + 1])

        #convert ex in list because django session doesn't accept arrays
        for element in self.ex:
            self.ex_list.append(element)

        #convert ex in list because django session doesn't accept arrays
        for element in self.hy:
            self.hy_list.append(element)

    def pulse_calculator(self, pulse, time_step):

        if pulse == 'gauss':
            return exp(-0.5 * ((self.t0 - time_step) / self.spread) ** 2)