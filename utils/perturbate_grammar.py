from faker import Faker
import random

def perturbate(rules, additional_rules: int = 100, n_rhss: int = 5, terminal_prod_p: float = 0.2):
  fake = Faker()
  added = list()
  for _ in range(additional_rules):
    lhs = fake.word()
    added.append(lhs)
    for n_rhs in range(random.randint(1, n_rhss)):
      if random.random() < terminal_prod_p:
        rhs = fake.word()
      else:
        rhs_1, rhs_2 = fake.words(2)
        rhs = f"{rhs_1} {rhs_2}"
      
      if lhs not in rules:
        rules[lhs] = list()
      rules[lhs].append(rhs)
    
  return rules, added
      