package dev.wilyjeb.geology.domain;

/** One latch per server, retained through shutdown for client presentation. */
public final class FailureState {
    private final java.util.concurrent.atomic.AtomicReference<GeologyFailure> failure =
            new java.util.concurrent.atomic.AtomicReference<>();
    private volatile boolean stopping;
    public GeologyFailure record(GeologyFailure value) {
        failure.compareAndSet(null, value);
        return failure.get();
    }
    public GeologyFailure failure() { return failure.get(); }
    public void stopping() { stopping = true; }
    public void check() {
        var value = failure.get();
        if (!stopping && value != null) throw value;
    }
}
