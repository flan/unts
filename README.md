unts was a term project for an Emergent Computing class taught by [Dr. Christian Jacob](http://pages.cpsc.ucalgary.ca/~jacob/HomeCJ/Christians_Home_Page/Home.html) in 2008. It was built using [Python](http://www.python.org/) 2.3 and [Breve](http://www.spiderland.org/) 2.7.2. It is extensively documented and should be a suitable starting point for other students looking for project platforms or inspiration.

unts is a relatively massive, highly flexible emergence framework and technical demonstration that simulates multiple ant-like colonies that search for food and water, reproduce, establish new hills, fight off menacing spider-like enemies, and battle amongst themselves for control of resources, all based on local environmental information without any sort of centralized AI or explicit communication mechanics.


---

# Overview #
This project's outline and implementation plan are summarized in its [proposal document](http://static.uguu.ca/projects/puukusoft/unts/data/System.pdf). It's a lengthy read, but most of the math can be ignored unless you plan to do more than simply change configuration values to see what will happen.

A [post-mortem write-up](http://static.uguu.ca/projects/puukusoft/unts/data/Conference.pdf) is also provided and should be consulted prior to using this system as a basis for other projects.


---

# Project information #
## Videos ##
  * [A short resource-gathering simulation](http://static.uguu.ca/projects/puukusoft/unts/data/swarming.avi) (1.2MB)
    * Notice how the workers gradually determine an optimum path to the resources, with disruptions as resources are depleted
  * [An example showing workers fleeing an attack](http://static.uguu.ca/projects/puukusoft/unts/data/scattering.avi) (2.6MB)
    * Observe how the workers are unable to form efficient paths and are effectively cornered by the warriors
  * [A demonstration of warriors defending workers from threats](http://static.uguu.ca/projects/puukusoft/unts/data/protection.avi) (3.2MB)
    * When the next reproduction cycle hits, the colony, knowing that it's vulnerable, emphasizes warrior production
  * [What happens when no warriors are around to save workers](http://static.uguu.ca/projects/puukusoft/unts/data/devastation.avi) (3.7MB)
    * Finding a great environment, the threats thrive and reproduce, decimating the colony's chances for survival
  * [A large simulation used to demonstrate the project](http://static.uguu.ca/projects/puukusoft/unts/data/simulation.avi) (26.7MB)
    * Unfortunately, this render was made against a buggy version (there wasn't time to fix it), so workers will actually assign a very low (reciprocal) score to resources within their core sense-of-smell radius. This results in the best-established colonies -- those that found new hills and seem to be thriving -- starving because they estimate that resource acquisition will occur faster than it does.
      * Despite this bug, there's a clear demonstration of emergent expansion, path-finding, defense (as warriors seek out threats based on lingering pheromones), avoidance, and a whole **ton** of math, demonstrating what can be done with a very simple configuration file and showing how small changes to the parameters of two colonies can produce dramatically different results, even with identical environments.
    * It's really pretty to watch.

## Development materials ##
 * [Class documentation](http://static.uguu.ca/projects/puukusoft/unts/api/)

### Getting help ###
If you're stuck or curious about how something works, don't hesitate to ask. You should get a response fairly quickly.


---

# Feedback #
If you found unts helpful in any way, let us know. If you really need a specific extension to make it work for you as part of a project, just ask. Emergence is a great field and we'd love to explore it with you.


---

# Credits #
[Neil Tallim](http://uguu.ca/)
  * Programming, design


---

# Contacts #
flan {at} uguu {dot} ca
