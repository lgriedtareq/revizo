import os
import random
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WAD2_Project.settings')
django.setup()

from revizo.models import UserProfile, Subject, Topic, Card, Explanation
from django.contrib.auth.models import User

def get_random_epoch_time(future=False):
     """Generate a random epoch time, either in the past or future."""
     now = datetime.now()
     if future:
         target_time = now + timedelta(days=random.randint(1, 14))
     else:
         target_time = now - timedelta(days=random.randint(1, 14))
     return int(target_time.timestamp())
 
def populate():
    # Clear existing data
    print("Clearing existing data...")
    Explanation.objects.all().delete()
    Card.objects.all().delete()
    Topic.objects.all().delete()
    Subject.objects.all().delete()
    UserProfile.objects.all().delete()
    User.objects.all().delete()
    print("Existing data cleared.")

    # Create test users
    users_data = [
         {"username": "student1", "email": "student1@example.com", "password": "pass123"},
         {"username": "student2", "email": "student2@example.com", "password": "pass456"},
         {"username": "student3", "email": "student3@example.com", "password": "pass789"}
     ]
 
    # Define meaningful subjects and their topics
    subjects_data = {
        "Computer Science": [
            "Python Programming",
            "Web Development",
            "Database Systems",
            "Algorithms & Data Structures",
            "Software Engineering"
        ],
        "Mathematics": [
            "Calculus",
            "Linear Algebra",
            "Statistics",
            "Discrete Mathematics",
            "Number Theory"
        ],
        "Physics": [
            "Classical Mechanics",
            "Electromagnetism",
            "Thermodynamics",
            "Quantum Physics",
            "Relativity"
        ],
        "Biology": [
            "Cell Biology",
            "Genetics",
            "Ecology",
            "Evolution",
            "Human Anatomy"
        ],
        "Chemistry": [
            "Organic Chemistry",
            "Inorganic Chemistry",
            "Physical Chemistry",
            "Biochemistry",
            "Analytical Chemistry"
        ]
    }
     
    for user_data in users_data:
         user, created = User.objects.get_or_create(
             username=user_data["username"],
             defaults={"email": user_data["email"]}
         )
         if created:
             user.set_password(user_data["password"])
             user.save()
         
         user_profile = UserProfile.objects.get_or_create(user=user)

         # Assign all subjects to each user instead of random selection
         for subject_name in subjects_data.keys():
             # Try to get existing subject for this user and subject name
             existing_subject = Subject.objects.filter(subject_name=subject_name, user=user).first()
             
             if not existing_subject:
                 subject = Subject.objects.create(
                     subject_name=subject_name,
                     user=user
                 )
             else:
                 subject = existing_subject
             
             # Get topics for this subject
             topics = subjects_data[subject_name]
             
             # Select random topics for this subject
             selected_topics = random.sample(topics, 3)
             
             for topic_name in selected_topics:
                 topic = Topic.objects.create(
                     topic_name=topic_name,
                     subject=subject
                 )
                 
                 # Create meaningful cards based on the topic
                 if topic_name == "Python Programming":
                     cards_data = [
                         ("What is a list comprehension in Python?", "A concise way to create lists based on existing lists or other iterables. Example: [x**2 for x in range(5)] creates [0, 1, 4, 9, 16]"),
                         ("What is the difference between append() and extend() in Python lists?", "append() adds a single element to the end of a list, while extend() adds all elements from an iterable to the end of a list."),
                         ("What is a decorator in Python?", "A function that takes another function as input and extends its behavior without explicitly modifying it. Used for adding functionality to existing functions.")
                     ]
                 elif topic_name == "Calculus":
                     cards_data = [
                         ("What is the derivative of x²?", "2x. The derivative represents the rate of change of a function at any point."),
                         ("What is the integral of 2x?", "x² + C, where C is the constant of integration."),
                         ("What is the chain rule?", "A rule for finding the derivative of a composite function. If y = f(g(x)), then dy/dx = f'(g(x)) * g'(x)")
                     ]
                 elif topic_name == "Cell Biology":
                     cards_data = [
                         ("What is the function of mitochondria?", "The powerhouse of the cell, responsible for producing ATP through cellular respiration."),
                         ("What is the difference between prokaryotic and eukaryotic cells?", "Prokaryotic cells lack a nucleus and membrane-bound organelles, while eukaryotic cells have both."),
                         ("What is the function of the cell membrane?", "Controls what enters and exits the cell, maintains cell shape, and provides protection.")
                     ]
                 elif topic_name == "Web Development":
                     cards_data = [
                         ("What is HTML?", "HyperText Markup Language - the standard language for creating web pages and web applications."),
                         ("What is CSS?", "Cascading Style Sheets - a style sheet language used for describing the presentation of a document written in HTML."),
                         ("What is JavaScript?", "A programming language that enables interactive web pages and is an essential part of web applications.")
                     ]
                 elif topic_name == "Database Systems":
                     cards_data = [
                         ("What is SQL?", "Structured Query Language - a standard language for storing, manipulating, and retrieving data in relational databases."),
                         ("What is a primary key?", "A column or set of columns in a table that uniquely identifies each row in the table."),
                         ("What is normalization?", "The process of organizing data to reduce redundancy and improve data integrity.")
                     ]
                 elif topic_name == "Algorithms & Data Structures":
                     cards_data = [
                         ("What is Big O notation?", "A mathematical notation that describes the performance or complexity of an algorithm."),
                         ("What is a binary search tree?", "A data structure where each node has at most two children, with values less than the parent on the left and greater on the right."),
                         ("What is quicksort?", "An efficient, in-place sorting algorithm that uses a divide-and-conquer strategy.")
                     ]
                 elif topic_name == "Software Engineering":
                     cards_data = [
                         ("What is Agile development?", "An iterative approach to software development that emphasizes flexibility, collaboration, and customer feedback."),
                         ("What is version control?", "A system that records changes to files over time, allowing you to track and revert changes if needed."),
                         ("What is unit testing?", "Testing individual components or functions of a program to ensure they work correctly in isolation.")
                     ]
                 elif topic_name == "Linear Algebra":
                     cards_data = [
                         ("What is a matrix?", "A rectangular array of numbers arranged in rows and columns."),
                         ("What is a determinant?", "A scalar value that can be computed from the elements of a square matrix."),
                         ("What is an eigenvector?", "A non-zero vector that changes by only a scalar factor when a linear transformation is applied.")
                     ]
                 elif topic_name == "Statistics":
                     cards_data = [
                         ("What is standard deviation?", "A measure of the amount of variation or dispersion in a set of values."),
                         ("What is a p-value?", "The probability of obtaining test results at least as extreme as the results actually observed."),
                         ("What is correlation?", "A statistical measure that describes the extent to which two variables change together.")
                     ]
                 elif topic_name == "Discrete Mathematics":
                     cards_data = [
                         ("What is a set?", "A collection of distinct objects, considered as an object in its own right."),
                         ("What is a function?", "A relation between a set of inputs and a set of permissible outputs."),
                         ("What is a graph?", "A mathematical structure used to model pairwise relations between objects.")
                     ]
                 elif topic_name == "Number Theory":
                     cards_data = [
                         ("What is a prime number?", "A natural number greater than 1 that is not a product of two smaller natural numbers."),
                         ("What is the greatest common divisor?", "The largest positive integer that divides each of the integers without a remainder."),
                         ("What is modular arithmetic?", "A system of arithmetic for integers where numbers wrap around upon reaching a certain value.")
                     ]
                 elif topic_name == "Classical Mechanics":
                     cards_data = [
                         ("What is Newton's First Law?", "An object will remain at rest or in uniform motion in a straight line unless acted upon by an external force."),
                         ("What is kinetic energy?", "The energy possessed by an object due to its motion."),
                         ("What is momentum?", "The product of an object's mass and velocity.")
                     ]
                 elif topic_name == "Electromagnetism":
                     cards_data = [
                         ("What is Coulomb's Law?", "The force between two charged particles is directly proportional to the product of their charges and inversely proportional to the square of the distance between them."),
                         ("What is Faraday's Law?", "The induced electromotive force in any closed circuit is equal to the negative of the time rate of change of the magnetic flux through the circuit."),
                         ("What is Ohm's Law?", "The current through a conductor between two points is directly proportional to the voltage across the two points.")
                     ]
                 elif topic_name == "Thermodynamics":
                     cards_data = [
                         ("What is the First Law of Thermodynamics?", "Energy cannot be created or destroyed, only transferred or converted from one form to another."),
                         ("What is entropy?", "A measure of the disorder or randomness in a system."),
                         ("What is specific heat capacity?", "The amount of heat energy required to raise the temperature of one unit mass of a substance by one degree.")
                     ]
                 elif topic_name == "Quantum Physics":
                     cards_data = [
                         ("What is wave-particle duality?", "The concept that every particle or quantum entity may be described as either a particle or a wave."),
                         ("What is the uncertainty principle?", "It is impossible to simultaneously know both the exact position and exact momentum of a particle."),
                         ("What is quantum entanglement?", "A physical phenomenon where two or more particles remain connected even when separated by large distances.")
                     ]
                 elif topic_name == "Relativity":
                     cards_data = [
                         ("What is the theory of relativity?", "A theory of space and time developed by Einstein, consisting of special and general relativity."),
                         ("What is time dilation?", "The difference in elapsed time as measured by two clocks, due to their relative velocity or gravitational potential."),
                         ("What is mass-energy equivalence?", "The principle that mass and energy are the same physical entity and can be converted into each other.")
                     ]
                 elif topic_name == "Genetics":
                     cards_data = [
                         ("What is DNA?", "Deoxyribonucleic acid - a molecule carrying genetic instructions for development, functioning, growth, and reproduction."),
                         ("What is a gene?", "A sequence of DNA that contains the instructions for making a specific protein or RNA molecule."),
                         ("What is mutation?", "A change in the DNA sequence that can lead to variations in traits.")
                     ]
                 elif topic_name == "Ecology":
                     cards_data = [
                         ("What is an ecosystem?", "A community of living organisms together with their physical environment."),
                         ("What is biodiversity?", "The variety of life in the world or in a particular habitat or ecosystem."),
                         ("What is a food chain?", "A linear network of links in a food web starting from producer organisms and ending at apex predator species.")
                     ]
                 elif topic_name == "Evolution":
                     cards_data = [
                         ("What is natural selection?", "The process where organisms better adapted to their environment tend to survive and produce more offspring."),
                         ("What is adaptation?", "A trait that helps an organism survive and reproduce in its environment."),
                         ("What is speciation?", "The formation of new and distinct species in the course of evolution.")
                     ]
                 elif topic_name == "Human Anatomy":
                     cards_data = [
                         ("What is the circulatory system?", "The system that circulates blood and lymph through the body, consisting of the heart, blood vessels, blood, and lymphatic vessels."),
                         ("What is the nervous system?", "The network of nerve cells and fibers that transmits nerve impulses between parts of the body."),
                         ("What is the respiratory system?", "The system responsible for taking in oxygen and expelling carbon dioxide.")
                     ]
                 elif topic_name == "Organic Chemistry":
                     cards_data = [
                         ("What is a hydrocarbon?", "A compound consisting entirely of hydrogen and carbon atoms."),
                         ("What is an isomer?", "Compounds with the same molecular formula but different structural arrangements."),
                         ("What is a functional group?", "A specific group of atoms within a molecule that is responsible for characteristic chemical reactions.")
                     ]
                 elif topic_name == "Inorganic Chemistry":
                     cards_data = [
                         ("What is an ionic bond?", "A chemical bond formed through the electrostatic attraction between oppositely charged ions."),
                         ("What is a covalent bond?", "A chemical bond that involves the sharing of electron pairs between atoms."),
                         ("What is an acid?", "A substance that donates protons or accepts electron pairs in reactions.")
                     ]
                 elif topic_name == "Physical Chemistry":
                     cards_data = [
                         ("What is thermodynamics?", "The study of energy and its transformations in chemical systems."),
                         ("What is kinetics?", "The study of the rates of chemical processes."),
                         ("What is quantum chemistry?", "The application of quantum mechanics to chemical systems.")
                     ]
                 elif topic_name == "Biochemistry":
                     cards_data = [
                         ("What is an enzyme?", "A protein that acts as a biological catalyst to speed up chemical reactions."),
                         ("What is metabolism?", "The set of life-sustaining chemical reactions in organisms."),
                         ("What is ATP?", "Adenosine triphosphate - the primary energy carrier in all living organisms.")
                     ]
                 elif topic_name == "Analytical Chemistry":
                     cards_data = [
                         ("What is chromatography?", "A technique for separating components of a mixture based on their different affinities for a stationary phase."),
                         ("What is spectroscopy?", "The study of the interaction between matter and electromagnetic radiation."),
                         ("What is titration?", "A technique for determining the concentration of a solution by adding a known concentration of another solution.")
                     ]
                 else:
                     # Default cards for any remaining topics
                     cards_data = [
                         (f"What is the main concept of {topic_name}?", f"Key concept 1 for {topic_name}"),
                         (f"What are the applications of {topic_name}?", f"Key application 1 for {topic_name}"),
                         (f"What are the fundamental principles of {topic_name}?", f"Key principle 1 for {topic_name}")
                     ]
                 
                 for front, back in cards_data:
                     card = Card.objects.create(
                         card_front=front,
                         card_back=back,
                         topic=topic
                     )
                     
                     # Add AI explanations for some cards
                     if random.choice([True, False]):
                         Explanation.objects.create(
                             ai_explanation=f"AI generated explanation for {front}",
                             card=card
                         )
 
if __name__ == "__main__":
    print("Starting population script...")
    populate()
    print("Database populated successfully!")
