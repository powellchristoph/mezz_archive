%rebase base
<p>The below assets are being retrieve from tape. This may take a while depending on the 
number of assets requested and the size of the asset. The recovery process starts very 5 minutes, so 
please be patient.</p>
<p>The recovery file will be copied to <strong>\\burbstor001\ifs\storagearray\vod\Archive\MEZZ_RESTORES.</strong><p>
<p>Please refresh the main page periodically to see the status of your transfer.</p>

<hr>
<p><strong>{{data['provider']}}</strong></p>
%for a in data['assets']:
<p>{{a}}</p>
%end
</br>
<hr>
<a href="/mezz/" class="btn btn-primary">Home</a>
