package uz.sarik.wormcinema

import android.annotation.SuppressLint
import android.app.Activity
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private val mainHandler = Handler(Looper.getMainLooper())

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.mediaPlaybackRequiresUserGesture = false
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean = false
            }
        }
        setContentView(webView)
        startLocalServer()
    }

    private fun startLocalServer() {
        Executors.newSingleThreadExecutor().execute {
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(application))
            }
            Python.getInstance()
                .getModule("start_server")
                .callAttr("start", filesDir.absolutePath)
        }
        // Flask needs a brief moment to bind its loopback-only port before WebView loads it.
        mainHandler.postDelayed({ webView.loadUrl("http://127.0.0.1:8765/") }, 700)
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }
}
