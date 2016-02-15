package com.example.jurko.qrreader2;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;

import com.google.zxing.integration.android.IntentIntegrator;

/**
 * Created by Jurko on 13. 2. 2016.
 */
public class Intro extends Activity implements View.OnClickListener {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.d("intro","onCreate");
        super.onCreate(savedInstanceState);
        Log.d("intro","onCreate");
        setContentView(R.layout.intro);

        Log.d("intro","onCreate3");
        Intent i = new Intent(getBaseContext(),MainActivity.class);
        startActivity(i);

    }
    @Override
    public void onClick(View v) {
        Log.d("intro","onCreate-onclick");
        Intent i = new Intent(getBaseContext(),MainActivity.class);
        startActivity(i);
    }
}
