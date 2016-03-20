package com.example.jurko.qrreader2;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import com.google.zxing.integration.android.IntentIntegrator;

/**
 * Created by Jurko on 13. 2. 2016.
 */
public class Intro extends Activity implements View.OnClickListener {


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.intro);

        Log.d("intro", "onCreate");
        ImageView logo = (ImageView) this.findViewById(R.id.imageView);


        View.OnClickListener viewListener = new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent i = new Intent(getBaseContext(),MainActivity.class);
                startActivity(i);
            }
        };
        logo.setOnClickListener(viewListener);
    }
    @Override
    public void onClick(View v) {
        Log.d("intro","onCreate-onclick");
        Intent i = new Intent(getBaseContext(),MainActivity.class);
        startActivity(i);
    }
}
