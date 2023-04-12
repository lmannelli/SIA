import numpy as np

global goal

import utils
import genetic

rng = np.random.default_rng()

def main():
  # palette = utils.get_colors("./colores.csv")
  file_name = input("Insert the name of the file: ")
  palette = utils.get_colors("./" + file_name + ".csv")
  print("Palette:")
  print(palette.shape)
  print(palette)
  goal = np.array([int(x) for x in input("Objective Color: ").split(',')], dtype=np.uint8)

  selector = genetic.SelectOption.RANKING
  selection_method = int(input("1-Roulette\n2-Elite\n3-Tourney\n4-Ranking\nInsert the selection method: "))
  if(selection_method == 1):
    selector = genetic.SelectOption.ROULETTE
  elif(selection_method == 2):
    selector = genetic.SelectOption.ELITE
  elif(selection_method == 3):
    selector = genetic.SelectOption.TOURNEY

  cross_method = genetic.CrossOption.UNIFORM  
  crossover_probability = int(input("1-Simple\n2-Doble\n3-Unforme\nInsert the probability of crossover: "))
  if(crossover_probability == 1):
    cross_method = genetic.CrossOption.SIMPLE
  elif(crossover_probability == 2):
    cross_method = genetic.CrossOption.DOUBLE

  # POBLACION INICIAL
  # population = 100
  population = int(input("Insert the population size: "))
  #se genera un array de la forma [[R1,G1,B1],[R2,G2,B2],...] con valores eleatorios uniformes 
  pop = rng.uniform(0., 1., size=(population, len(palette)))
  
  iter_amount= int(input("Insert iteration amount: "))
  end = False
  # delta = 0.01
  delta = float(input("Insert DELTA for cut condition (1-fitness < DELTA): "))
  i = 0 

  while (not end):
    print("iteracion: " + str(i))

    rgbp = utils.get_rgbp(palette, pop)
    mixes = utils.get_mixes(rgbp)

    # check criteria
    end = utils.check_finished(iter_amount, i, pop, mixes, delta, goal)

    # SELECTION
    parents = selector(pop, mixes, genetic.aptitud, population, goal)

    # CROSSOVER
    children = genetic.cross_n(parents, cross_method)

    newpop = children if len(children) == population else np.concatenate((children, parents[:(population - len(children))]), axis=0)

    # MUTATION
    newpop = genetic.mutate_n(newpop)

    pop = newpop

    i += 1



if __name__ == '__main__':
  main()