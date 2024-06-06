import numpy as np
from sklearn.linear_model import LinearRegression

# The hovering time is based on flying at 10 m above sea level in a no-wind environment and landing with 10% battery level.



# battery TB47S
#payload = np.array([0.4, 0.9, 1.8, 6]).reshape((-1, 1))
#hovering_time = np.array([30,28,23,16])

# B [Ws = J], delta [s], alpha [W]
# B [percentuale], delta [s], alpha [percentuale/s]

#
B = 90 # %
# battery TB48S
# B = (467856 * 6) * 0.9 # Ws per 6 batterie
#0.5, 0.9, 1.9,
#35,34,29
payload = np.array([0, 5.5]).reshape((-1, 1)) # kg
delta_max = np.array([38, 18]) * 60 # seconds
alpha = B / delta_max



# we are interested in expressing the equation alpha(payload) = m * payload + q



#unit_consumption = 1/(hovering_time*60)
#print(unit_consumption)


model = LinearRegression().fit(payload, alpha)

q = model.intercept_
m = model.coef_
print('intercept:', q)
print('slope:', m)


payload = np.array([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
alpha_new = m * payload + q
delta_max = B / alpha_new
print("consumption rate:", alpha_new)
print("tempo:", delta_max)
#check = alpha.reshape((-1, 1))*60 * (q + m*payload)
#print(check)


