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
import android.view.KeyEvent;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;

public class MainActivity extends Activity implements View.OnClickListener {

    private Button scanBtn;
    private Button scanned;
    private TextView formatTxt, contentTxt;
    private String hashed;
    public final static String long_passwd = "com.example.jurko.qrreader2.hashed";

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

        //scanBtn.setBackgroundColor(3355444);
        //scanned.setBackgroundColor(3355444);
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
        }
        if(v.getId()==R.id.scanned){
            String qr = this.getSavedQr();
            this.hash_QR_Time(qr);

        }
    }

    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
//retrieve scan result
        Toast.makeText(getApplicationContext(), (String) "je v activity result", Toast.LENGTH_SHORT).show();
        IntentResult scanningResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
        if (scanningResult != null) {
//we have a result
            String scanContent = scanningResult.getContents();
            String scanFormat = scanningResult.getFormatName();
            this.saveQr(scanContent);

            //formatTxt.setText("FORMAT: " + scanFormat);
            //contentTxt.setText("CONTENT: " + scanContent);

            hash_QR_Time(scanContent);
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

    private void saveQr(String scanContent){
        SharedPreferences mPrefs = getSharedPreferences("label", 0);
        SharedPreferences.Editor mEditor = mPrefs.edit();
        mEditor.putString("tagQr", scanContent).commit();
    }




    public String hash_QR_Time(String seed){


        Time today = new Time(Time.TIMEZONE_UTC);

        today.setToNow();
        Toast.makeText(getApplicationContext(),  today.toString(), Toast.LENGTH_LONG).show();
        Hash hash = new Hash();
        hashed = hash.get_SHA_512_SecurePassword(today.toString() , seed);
        //Toast.makeText(getApplicationContext(),  hashed, Toast.LENGTH_LONG).show();
        Intent intent = new Intent(this, Main2Activity.class);
        intent.putExtra(long_passwd , hashed);
        startActivity(intent);
        return  hash.get_SHA_512_SecurePassword(today.toString() , seed);
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
