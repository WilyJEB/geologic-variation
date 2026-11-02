import ai.onnxruntime.OrtEnvironment;
import ai.onnxruntime.OrtSession;
import ai.onnxruntime.providers.OrtCUDAProviderOptions;

/** Native feasibility only: no Minecraft save, TD identity mutation or fallback. */
public final class BackendPreflight {
    public static void main(String[] args) throws Exception {
        System.out.println("JAVA " + System.getProperty("java.version") + " "
                + System.getProperty("os.name") + "/" + System.getProperty("os.arch"));
        try (var env = OrtEnvironment.getEnvironment(); var opts = new OrtSession.SessionOptions()) {
            System.out.println("NATIVE_INITIALIZED providers=" + OrtEnvironment.getAvailableProviders());
            if (args[0].equals("cuda")) {
                try (var cuda = new OrtCUDAProviderOptions(0)) {
                    cuda.add("arena_extend_strategy", "kSameAsRequested");
                    cuda.add("cudnn_conv_algo_search", "HEURISTIC");
                    cuda.add("do_copy_in_default_stream", "1");
                    opts.addCUDA(cuda);
                }
            } else if (args[0].equals("directml")) {
                opts.addDirectML(0);
            } else if (!args[0].equals("cpu")) {
                throw new IllegalArgumentException("Expected cpu, cuda or directml");
            }
            System.out.println("PROVIDER_ADDED " + args[0]);
            try (var session = env.createSession(args[1], opts)) {
                System.out.println("MODEL_SESSION_CREATED inputs=" + session.getInputInfo());
            }
        }
    }
}
