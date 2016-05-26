package com.example.jurko.qrreader2;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.design.widget.Snackbar;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.format.Time;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;

import java.io.Serializable;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.TimeZone;

public class MainActivity extends Activity implements View.OnClickListener {

    private Button scanBtn;
    private Button scanned;
    private TextView formatTxt, contentTxt;
    private String hashed;
    public final static String long_passwd = "com.example.jurko.qrreader2.hashed";
    public final static String qr = "savedQr";
    public final static String mobileTime = "savedMtime";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        //setSupportActionBar(toolbar);

        scanBtn = (Button)findViewById(R.id.scan_button);
        //formatTxt = (TextView)findViewById(R.id.scan_format);
        //contentTxt = (TextView)findViewById(R.id.scan_content);
        scanned = (Button)findViewById(R.id.scanned);

        scanBtn.setOnClickListener(this);
        scanned.setOnClickListener(this);

        // exiting
        if (getIntent().getBooleanExtra("EXIT", false)) {
            finish();
            return;
        }


    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onClick(View v) {
        if(v.getId()==R.id.scan_button){ //scan
            IntentIntegrator scanIntegrator = new IntentIntegrator(this);
            scanIntegrator.initiateScan();
            Log.d("cas", "current system time while scanning " + String.valueOf(this.roundSystemTime()));
        }
        if(v.getId()==R.id.scanned){
            String id = this.getSavedQr().substring(this.getSavedQr().lastIndexOf("#") + 1);
            Log.d("cas", "current system time without rounding" + String.valueOf(System.currentTimeMillis()));
            this.hash_QR_Time(id + Long.toString(this.countServerTime()).substring(0,8));

        }
    }

    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
        //retrieve scan result
        IntentResult scanningResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
        if (scanningResult.getContents() != null) {
            //we have a result
            String scanContent = scanningResult.getContents();
            this.saveQr(scanContent);
            this.saveMobileTime(this.roundSystemTime());
        } else {
            Toast toast = Toast.makeText(getApplicationContext(),
                    "No scan data received!", Toast.LENGTH_SHORT);
            toast.show();
        }
    }

    private String getSavedQr(){
        SharedPreferences mPrefs = getSharedPreferences("label", 0);
        String mString = mPrefs.getString("tagQr", "default_value_if_variable_not_found");
        return mString;
    }

    private long getSavedMobileTime(){
        SharedPreferences mPrefs = getSharedPreferences("label", 0);
        long def = 0;
        long mLong = mPrefs.getLong("mobileTime", def );
        return mLong;
    }

    private void saveMobileTime(long mobileTime){
        SharedPreferences mPrefs = getSharedPreferences("label", 0);
        SharedPreferences.Editor mEditor = mPrefs.edit();
        mEditor.putLong("mobileTime", mobileTime ).commit();
    }

    private void saveQr(String scanContent){
        SharedPreferences mPrefs = getSharedPreferences("label", 0);
        SharedPreferences.Editor mEditor = mPrefs.edit();
        mEditor.putString("tagQr", scanContent).commit();
    }

    private long countServerTime(){
        long timePassed = this.roundSystemTime() - this.getSavedMobileTime(); //time passed from first scan
        Log.d("cas", " time in time of scan "  + String.valueOf(this.getSavedMobileTime()));
        Log.d("cas", "current system time "  +  String.valueOf(this.roundSystemTime()));
        Log.d("cas", "current system time without rounding" + String.valueOf(System.currentTimeMillis()));
        Log.d("cas", "timePassed " + String.valueOf(timePassed));
        Log.d("cas", "timeOnServer " + String.valueOf(Long.valueOf(this.getSavedQr().substring(0, this.getSavedQr().lastIndexOf("#"))) + timePassed));
        Log.d("cas", "data in QR code " + this.getSavedQr());
        Long serverTime = Long.valueOf(this.getSavedQr().substring(0, this.getSavedQr().lastIndexOf("#"))) + timePassed; //time in QR code + timePassed
        return serverTime;

    }
    public long roundSystemTime(){ // aby mal cas 10 cifier vsade, sekundova presnost, zaokruhli sa neskor
        return System.currentTimeMillis() / 1000;
    }




    public String hash_QR_Time(String myTime){

        Hash hash = new Hash(this.getSavedQr(), this.getSavedMobileTime());
        Log.d("cas", "ide sa hesovat " + myTime);
        hashed = hash.get_SHA_512_SecurePassword(myTime);
        Log.d("cas", "hashed time" + hashed);
        Log.d("cas", "byte array" + String.valueOf(hash.get_SHA_512_SecurePassword( myTime)));
        //Toast.makeText(getApplicationContext(),  hashed, Toast.LENGTH_LONG).show();
        Hash newPasswd = new Hash(this.getSavedQr(), this.getSavedMobileTime());
        Intent intent = new Intent(this, Main2Activity.class);
        intent.putExtra(long_passwd , hashed);
        intent.putExtra(qr, this.getSavedQr());
        intent.putExtra(mobileTime, this.getSavedMobileTime());

        startActivity(intent);
        return  hashed;
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK ) {
            Intent intent = new Intent(MainActivity.this, MainActivity.class);
            intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
            intent.putExtra("EXIT", true);
            startActivity(intent);
        }
        return super.onKeyDown(keyCode, event);
    }
}
