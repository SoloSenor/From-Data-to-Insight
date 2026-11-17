class Reading:
    def __init__(self, value):
        self.value = value

original = Reading(12)
alias = original
independent = Reading(original.value)
alias.value = 15
print(original.value, independent.value)
print(alias is original)
