package dev.wilyjeb.geology;

import dev.wilyjeb.geology.domain.FailureState;

/** Implemented on each MinecraftServer by the lifecycle mixin. */
public interface GeologyServer {
    FailureState geology$failures();
}
