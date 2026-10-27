package dev.wilyjeb.geology;

import dev.wilyjeb.geology.domain.FailureState;

/** Server ownership for chunk-worker cancellation. */
public interface GeologyChunks {
    FailureState geology$failures();
}
