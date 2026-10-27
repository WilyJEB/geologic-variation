package dev.wilyjeb.geology;

/** Client-only handoff; implementations never access UI on the server thread. */
public interface GeologyClient {
    void geology$recover(net.minecraft.client.server.IntegratedServer server);
}
