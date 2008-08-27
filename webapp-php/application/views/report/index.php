<?php slot::start('head') ?>
    <title>[@ <?php out::H($report->signature) ?> ] - <?php out::H($report->product) ?> <?php out::H($report->version) ?> Crash Report - Report ID: <?php out::H($report->uuid) ?></title>

    <?php echo html::stylesheet(array(
        'css/flora/flora.all.css'
    ), 'screen')?>

    <?php echo html::script(array(
        'js/jquery/jquery-1.2.1.js',
        'js/jquery/plugins/ui/ui.tabs.js'
    ))?>

  <script type="text/javascript">
      $(document).ready(function(){
        $('#report-index > ul').tabs();
        $('#showallthreads').removeClass('hidden').click(function(){
        $('#allthreads').toggle(400);
          return false;
        });
        $('.signature-column').append(' <a class="expand" href="#">[Expand]</a>');
        $('.expand').click(function(){
          // swap cell title into cell text for each cell in this column
          $("td:nth-child(3)", $(this).parents('tbody')).each(function(){
            $(this).text($(this).attr('title')).removeAttr('title');
          });
          $(this).remove();
          return false;
        });
      });
  </script> 

<?php slot::end() ?>

<h1 id="report-header" class="first"><?php out::H($report->product) ?> <?php out::H($report->version) ?> Crash Report [@ <?php out::H($report->signature) ?> ]</h1>
<div id="report-header-details">ID: <span><?php out::H($report->uuid) ?></span><br/> Signature: <span><?php out::H($report->signature) ?></span></div>
<div id="report-index" class="flora">

    <ul>
        <li><a href="#details"><span>Details</span></a></li>
        <li><a href="#frames"><span>Frames</span></a></li>
        <li><a href="#modules"><span>Modules</span></a></li>
        <li><a href="#rawdump"><span>Raw Dump</span></a></li>
    </ul>
    <div id="details">
        <table class="list record">
            <tr class="odd">
                <th>Signature</th><td><?php out::H($report->signature) ?></td>
            </tr>
            <tr class="even">
                <th>UUID</th><td><?php out::H($report->uuid) ?></td>
            </tr>
            <tr class="odd">
                <th>Time</th><td><?php out::H($report->date) ?></td>
            </tr>
            <tr class="even">
                <th>Uptime</th><td><?php out::H($report->uptime) ?></td>
            </tr>
            <tr class="odd">
                <th>Product</th><td><?php out::H($report->product) ?></td>
            </tr>
            <tr class="even">
                <th>Version</th><td><?php out::H($report->version) ?></td>
            </tr>
            <tr class="odd">
                <th>Build ID</th><td><?php out::H($report->build) ?></td>
            </tr>
            <tr class="even">
                <th>OS</th><td><?php out::H($report->os_name) ?></td>
            </tr>
            <tr class="odd">
                <th>OS Version</th><td><?php out::H($report->os_version) ?></td>
            </tr>
            <tr class="even">
                <th>CPU</th><td><?php out::H($report->cpu_name) ?></td>
            </tr>
            <tr class="odd">
                <th>CPU Info</th><td><?php out::H($report->cpu_info) ?></td>
            </tr>
            <tr class="even">
                <th>Crash Reason</th><td><?php out::H($report->reason) ?></td>
            </tr>
            <tr class="odd">
                <th>Crash Address</th><td><?php out::H($report->address) ?></td>
            </tr>
            <tr class="even">
                <th>Comments</th><td><?php out::H($report->comments) ?></td>
            </tr>
        </table>
    </div>

    <div id="frames">
        <?php if (count($report->threads)): ?>
           
            <?php function stack_trace($frames) { ?>
                <table class="list" py:def="stack_trace(frames)">
                    <tr>
                        <th>Frame</th>
                        <th>Module</th>
                        <th class="signature-column">Signature</th>
                        <th>Source</th>
                    </tr>
                    <?php $row = 1 ?>
                    <?php foreach ($frames as $frame): ?>
                        <tr class="<?php echo ( ($row-1) % 2) == 0 ? 'even' : 'odd' ?>">
                            <td><?php out::H($frame['frame_num']) ?></td>
                            <td><?php out::H($frame['module_name']) ?></td>
                            <td title="<?php out::H($frame['signature']) ?>"><?php out::H($frame['short_signature']) ?></td>
                            <td>
                                <a href="<?php out::H($frame['source_link']) ?>"><?php out::H($frame['source_info']) ?></a>
                            </td>
                        </tr>
                        <?php $row += 1 ?>
                    <?php endforeach ?>
                </table>
            <?php } ?>

            <h2>Crashing Thread</h2>
            <?php stack_trace($report->threads[$report->crashed_thread]) ?>

            <p id="showallthreads" class="hidden"><a href="#allthreads">Show/hide other threads</a></p>
            <div id="allthreads">
                <?php for ($i=0; $i<count($report->threads); $i++): ?>
                    <?php if ($i == $report->crashed_thread) continue; ?>
                    <h2>Thread <?php out::H($i) ?></h2>
                    <?php stack_trace($report->threads[$i]) ?>
                <?php endfor ?>
            </div>

            <script>document.getElementById("allthreads").style.display="none";</script>

        <?php endif ?>
    </div>

    <div id="modules">
        <?php if (count($report->modules)): ?>
        <table class="list">
            <tr>
                <th>Filename</th>
                <th>Version</th>
                <th>Debug Identifier</th>
                <th>Debug Filename</th>
            </tr>
            <?php $row = 1 ?>
            <?php foreach ($report->modules as $module): ?>
                <tr class="<?php echo ( ($row-1) % 2) == 0 ? 'even' : 'odd' ?>">
                    <td><?php out::H($module['filename']) ?></td>
                    <td><?php out::H($module['module_version']) ?></td>
                    <td><?php out::H($module['debug_id']) ?></td>
                    <td><?php out::H($module['debug_filename']) ?></td>
                </tr>
                <?php $row += 1 ?>
            <?php endforeach ?>
        </table>
    <?php endif ?>
    </div>

    <div id="rawdump">
        <div class="code"><?php out::H($report->dump) ?></div>
    </div>

</div>