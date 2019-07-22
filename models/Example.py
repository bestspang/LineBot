class Employee:
    def __init__(self, name, id, line_id):
        self.name = name
        self.id = id
        self.line_id = line_id
        self.marks = []

    def average(self):
        return sum(self.marks) / len(self.marks)

    @classmethod
    def friend(cls, origin, friend_name, *args, **kwargs):
        return cls(friend_name, origin.salary, *args, **kwargs)

####

class AddEmployee(Employee):
    def __init__(self, name, id, line_id, salary, job_title):
        super().__init__(name, id, line_id)
        self.salary = salary
        self.job_title = job_title

best = AddEmployee("Best", 1, "a", 15000, "R&D Director")
print(best.name)
print(best.salary)
print(best.id)
print(best.line_id)
print(best.job_title)
print("+++")
taan = AddEmployee.friend(best, "Taan", 2, "b", job_title="CTO")
print(taan.name)
print(taan.salary)
print(taan.id)
print(taan.line_id)
print(taan.job_title)
