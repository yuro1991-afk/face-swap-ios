import SwiftUI
import WebKit

/// WKWebView shell. This is source only on Windows.
/// Build it in Xcode on a Mac. It is not a signed IPA in git.
struct ContentView: View {
    @AppStorage("gatewayURL") private var gatewayURL = "http://192.168.1.102:8860"

    var body: some View {
        VStack(spacing: 0) {
            GatewayWebView(urlString: gatewayURL)
            TextField("Gateway URL", text: $gatewayURL)
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .font(.footnote)
                .padding(8)
        }
        .ignoresSafeArea(edges: .top)
    }
}

struct GatewayWebView: UIViewRepresentable {
    let urlString: String

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        let view = WKWebView(frame: .zero, configuration: config)
        view.scrollView.contentInsetAdjustmentBehavior = .never
        return view
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        guard let url = URL(string: urlString), uiView.url != url else { return }
        uiView.load(URLRequest(url: url))
    }
}
