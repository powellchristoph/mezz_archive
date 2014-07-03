%rebase base
<h3><a href="/mezz/">Archive</a> -> {{data['provider']}}</h3>
%if not data['assets']:
<h5>There are no assets.</h5>
%else:
  <form action="/mezz/get/" method="POST">
    <fieldset>
      <input type="hidden" value="{{data['provider']}}" name="provider" />
      %for p in data['assets']:
        <label class="checkbox">
          <input value="{{p}}" type="checkbox" name="assets">{{p}}
        </label>
      %end
      <div class="form-actions">
        <button type="submit" class="btn btn-primary">Retrieve assets</button> or
        <a href="/mezz/" type="button" class="btn">Cancel</a>
    </fieldset>
  </form>
%end
