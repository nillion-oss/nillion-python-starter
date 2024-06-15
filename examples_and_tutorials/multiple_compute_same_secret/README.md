# Single Party Compute Examples

This example demonstrates how to run multiple programs on the same stored secret.

In particular, we run a basic addition (two inputs) and multiplication (two inputs) on the same stored secret.

The trick here is to not provide bindings at the time of storing the secret, instead only provide permissions. We then provide compute bindings at computation time for the different programs.