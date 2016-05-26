package com.example.jurko.qrreader2;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Arrays;

public class Main2Activity extends Activity implements View.OnClickListener {

    public final static String long_passwd = "com.example.jurko.qrreader2.hashed";
    public final static String qr = "savedQr";
    public final static String mobileTime = "savedMtime";
    private TextView passwd;
    private Button newPasswd;
    public int boundary = 8;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);

        passwd = (TextView)findViewById(R.id.textView2);


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
        if(v.getId()==R.id.newPasswd){
            Intent intent = getIntent();
            String qrCode = intent.getStringExtra(Main2Activity.qr);
            long mobileTime = intent.getLongExtra(Main2Activity.mobileTime , 0);

            Hash hash = new Hash(qrCode, mobileTime);
            long serverTime =  Long.valueOf(qrCode.substring(0, qrCode.lastIndexOf("#"))) + (hash.roundSystemTime() - mobileTime);
            String tohash = qrCode.substring(qrCode.lastIndexOf("#") + 1) + Long.toString(serverTime).substring(0,8);
            Log.d("noveHeslo" , "tohash " + tohash);
            String hashed = hash.get_SHA_512_SecurePassword(tohash);
            passwd.setText(hashed.substring(0,this.boundary));
        }
    }


}
