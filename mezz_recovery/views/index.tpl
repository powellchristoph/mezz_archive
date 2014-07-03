%rebase base
<h3>Archived Affiliates</h3>
<ul>
%for p in data['providers']:
<li><a href="{{p}}/">{{p}}</a></li>
%end
</ul>

</br>
<p>Recovered file are copied to</p>
<p><strong>\\burbstor001\ifs\storagearray\vod\Archive\MEZZ_RESTORES</strong></p>
</br>
<table class="table table-striped">
  <caption><strong>Recovered Assets</strong></caption>
  <thead>
    <tr>
      <th>Asset</th>
      <th>Status</th>
      <th>Submitted</th>
      <th>Started</th>
      <th>Completed</th>
    </tr>
  </thead>
  <tbody>
    %if not data['rows']:
    <tr>
      <td>No assets have been recovered.</td>
    </tr>
    %else:
      %for row in data['rows']:
      <tr>
        %for col in row:
        <td>{{col}}</td>
        %end
      </tr>
      %end
    %end
  </tbody>
</table>

