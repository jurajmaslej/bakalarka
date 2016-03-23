package com.example.jurko.qrreader2;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
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
    private Button newPasswd;
    public int boundary = 6;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);
        passwd = (TextView)findViewById(R.id.textView2);
        longerPasswd = (Button)findViewById(R.id.longerPasswd);
        longerPasswd.setOnClickListener(this);

        newPasswd = (Button)findViewById(R.id.newPasswd);
        newPasswd.setOnClickListener(this);
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
            if (this.boundary < 14) {
                this.boundary += 1;
                this.showPasswd();
            }
        }
        if(v.getId()==R.id.newPasswd){
            Hash hash = new Hash();
            String time = hash.getTime(10000); //10 seconds
            String hashed = hash.get_SHA_512_SecurePassword(time , this.getSavedQr());
            passwd.setText(hashed.substring(0,this.boundary));
        }
    }

    private String getSavedQr(){
        SharedPreferences mPrefs = getSharedPreferences("label", 0);
        String mString = mPrefs.getString("tagQr", "default_value_if_variable_not_found");
        return mString;
    }
}
