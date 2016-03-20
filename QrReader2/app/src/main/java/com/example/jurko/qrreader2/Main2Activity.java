package com.example.jurko.qrreader2;

import android.app.Activity;
import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Arrays;

public class Main2Activity extends Activity implements View.OnClickListener {

    public final static String long_passwd = "com.example.jurko.qrreader2.hashed";
    private TextView passwd;
    private Button longerPasswd;
    public int boundary = 6;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);
        passwd = (TextView)findViewById(R.id.textView2);
        longerPasswd = (Button)findViewById(R.id.longerPasswd);
        longerPasswd.setOnClickListener(this);
        showPasswd();
        //

    }

    protected String shortenPasswd(int length){
        Intent intent = getIntent();
        String longPasswd = intent.getStringExtra(Main2Activity.long_passwd);
        return  longPasswd.substring(0, length);

    }

    public void showPasswd(){
        String shortPasswd = shortenPasswd(this.boundary);
        passwd.setText(shortPasswd);

    }

    @Override
    public void onClick(View v) {
        if(v.getId()==R.id.longerPasswd){
            if (this.boundary < 10) {
                this.boundary += 1;
                this.showPasswd();
            }
        }
    }
}
