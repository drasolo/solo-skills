# Other systems catalog

Reinforcement learning, probabilistic and causal models, and the procedure for any system not covered elsewhere.

## Reinforcement learning

Decision branches: what the reward stands in for, whether a scripted policy reaches the bar, how the simulator differs from reality, and what an unsafe action costs during exploration.

- **Reward hacking.** High reward with bad behavior. Watch full episodes and track a separate true-goal metric. (Evidence)
- **No simple policy baseline.** Compare with random and scripted policies. (Evidence)
- **Too few seeds.** Deep RL results vary widely between seeds. Report intervals over many seeds. (Evidence)
- **Eval on training seeds.** Hold out environment seeds and level layouts. (Evidence)
- **Truncation treated as termination.** Time limits must bootstrap the value, where true terminal states do not. (Mechanics)
- **Unsaved normalization.** Observation statistics are lost at load time or keep updating in eval. (Mechanics)
- **Exploration left on in eval.** Report deterministic and stochastic behavior deliberately. (Mechanics)
- **Sim-to-real gap.** Test with randomized dynamics and start with a shielded real-world rollout. (Exposure)

## Probabilistic models

Decision branches: which prior beliefs are defensible and which decision uses the posterior.

- **Unconverged inference.** Check R-hat, effective sample size and divergences. (Evidence)
- **No posterior predictive check.** Compare simulated data with observed data. (Evidence)
- **Prior sensitivity unknown.** Refit under other reasonable priors and report the change. (Evidence)
- **Interval miscalibration.** Measure coverage on held-out data. (Evidence)

## Causal models

Decision branches: what intervention is considered, and whether an experiment is possible.

- **Unstated assumptions.** Write the causal graph and name the unobserved confounders. (Evidence)
- **Conditioning on a collider or mediator.** Check every adjustment variable against the graph. (Mechanics)
- **No overlap.** Some groups never receive a treatment. Check propensity distributions. (Evidence)
- **No refutation test.** Run placebo treatments and sensitivity analysis. (Evidence)

## Procedure for an unlisted system

For anything else, such as a new architecture, embedded inference, federated training, scientific ML, or a hybrid, write a catalog before step 3. Answer each question for this specific system and turn every answer into a named failure entry assigned to an axis:

1. What information can reach the model during training or evaluation that it won't have in use?
2. What can score well while failing the real goal?
3. Which steps can fail without raising an error?
4. What varies between runs, and how large is that variation compared to the claimed effect?
5. What is the simplest alternative that could reach the bar?
6. How does input in use differ from input in evaluation, and who can control it?
7. What is the worst irreversible result of a wrong output?

Search primary sources for known failures of this method. Add the derived entries to the sub-agent prompts in step 4.
