package dev.wilyjeb.geology.domain;

/** A tagged failure: only these errors may bypass the client's fatal crash screen. */
public final class GeologyFailure extends RuntimeException {
    public GeologyFailure(String message, Throwable cause) { super(message, cause); }

    public String userMessage() {
        String summary = "The world's geology settings or terrain inference could not be verified.";
        var seen = java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<Throwable, Boolean>());
        for (Throwable cause = this; cause != null && seen.add(cause); cause = cause.getCause())
            if (cause instanceof GenerationContext.Mismatch mismatch) {
                summary = "Incompatible geology: " + mismatch.fields() + ".";
                break;
            }
        return summary + "\nRestore the original installation and world inputs. Do not edit or delete the geology snapshot."
                + "\nSee logs/latest.log for the full diagnostic. Changes since the last save may be lost.";
    }

    public static GeologyFailure find(Throwable cause) {
        var seen = java.util.Collections.newSetFromMap(new java.util.IdentityHashMap<Throwable, Boolean>());
        while (cause != null && seen.add(cause)) {
            if (cause instanceof GeologyFailure failure) return failure;
            cause = cause.getCause();
        }
        return null;
    }
}
