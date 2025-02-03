import './styles.css';

export default function ProfileSettings() {
    return (
        <div className="wrap">
        <div className="main_title">Настройки группы</div>
        <div className="container">
            <div className="title">Главная информация</div>

            {/* <div className="group_name">
                <div className="mini_title">Название группы</div>
                <input className="inp"/>
            </div>
            <div className="description">
                <div className="mini_title">Краткое описание</div>
                <input className="big_inp"/>
            </div>
            <div className="serv_avatar">
                <div className="mini_title">Изображение сервера</div>
                <div className="serv_photo_prev"></div>
                <button className="upload_serv_avatar">Загрузить</button>
            </div> */}
            <div className="panorama">
                <div className="mini_title">Панорама</div>
                <div className="serv_panorama_prev"></div>
                <button className="upload_serv_panorama">Загрузить</button>
            </div>
{/* 
            <div className="chat-actions">
                <h3>Каналы</h3>
                <button className="chat-action-btn">
                    <div className="bx">
                        <i className='bx bx-hash'></i>
                    </div>
                    <div className="bx2">
                        <span className="base-chanel-name"> Чат 1</span>
                    </div>
                    <div className="trash-bin">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path d="M6 7H5v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7H6zm10.618-3L15 2H9L7.382 4H3v2h18V4z"></path></svg>
                    </div>
                </button>
                <button className="chat-action-btn">
                    <div className="bx">
                        <i className='bx bx-hash'></i>
                    </div>
                    <div className="bx2">
                        <span className="base-chanel-name"> Чат 2</span>
                    </div>
                    <div className="trash-bin">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path d="M6 7H5v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7H6zm10.618-3L15 2H9L7.382 4H3v2h18V4z"></path></svg>
                    </div>
                </button>
                <button className="chat-action-btn">
                    <div className="bx">
                        <i className='bx bx-hash'></i>
                    </div>
                    <div className="bx2">
                        <span className="base-chanel-name"> Чат 3</span>
                    </div>
                    <div className="trash-bin">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"><path d="M6 7H5v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7H6zm10.618-3L15 2H9L7.382 4H3v2h18V4z"></path></svg>
                    </div>
                </button> */}
                {/* <div className="voice-channels">
                    <div className="voice-channel">
                        <div className="mic">
                            <i className='bx bxs-microphone'></i>
                            <span className="chanel-name"> Голосовой 1</span>
                        </div>
                        <div className="trash-bin">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" style="fill: rgb(145, 0, 0);"><path d="M6 7H5v13a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7H6zm10.618-3L15 2H9L7.382 4H3v2h18V4z"></path></svg>
                        </div>
                    </div>
                </div> */}
                {/* <button className="add_channel">Добавить</button> */}
            {/* </div>
  
            <div className="general">
                <div className="notifications">
                    <div className="name">Уведомления</div>
                    <div className="buttons">
                        <div className="on">Вкл</div>
                        <div className="off">Выкл</div>
                    </div>
                </div>
                <div className="theme">
                    <div className="name">Тема</div>
                    <div className="buttons">
                        <div className="dark">Тёмная</div>
                        <div className="light">Светлая</div>
                    </div>
                </div>
            </div> */}
    
{/*     
            // <div className="group-set">
                
            //     <div className="roles">
            //         <div className="act">
            //             <div className="name">Роли</div>
            //             <div className="buttons">
            //                 <div className="button-add">Добавить роль</div>
            //                 <div className="button-del">Удалить</div>
            //             </div>
            //         </div>
            //         <div className="tab">
            //             <div className="titler">Роли вашей группы:</div>
    
    
            //             <div className="role">
            //                 <div className="role-info">
            //                     <div className="role-color"></div>
            //                     <div className="role-name">Название роли</div>
            //                 </div>
            //                  <div className="role-info2">
            //                     !<-- <div className="count"><i className='bx bxs-user'></i> <div className="num">4</div></div> -->
            //                     <div className="status"><i className='bx bx-cog'></i></div>
            //                  </div>
            //             </div>
    
            //             <div className="role">
            //                 <div className="role-info">
            //                     <div className="role-color"></div>
            //                     <div className="role-name">Название роли</div>
            //                 </div>
            //                  <div className="role-info2">
            //                     <!-- <div className="count"><i className='bx bxs-user'></i> <div className="num">4</div></div> -->
            //                     <div className="status"><i className='bx bx-cog'></i></div>
            //                  </div>
            //             </div>
    
            //             <div className="role">
            //                 <div className="role-info">
            //                     <div className="role-color"></div>
            //                     <div className="role-name">Название роли</div>
            //                 </div>
            //                  <div className="role-info2">
            //                     <!-- <div className="count"><i className='bx bxs-user'></i> <div className="num">4</div></div> -->
            //                     <div className="status"><i className='bx bx-cog'></i></div>
            //                  </div>
            //             </div>
    
            //             <div className="role">
            //                 <div className="role-info">
            //                     <div className="role-color"></div>
            //                     <div className="role-name">Название роли</div>
            //                 </div>
            //                  <div className="role-info2">
            //                     <!-- <div className="count"><i className='bx bxs-user'></i> <div className="num">4</div></div> -->
            //                     <div className="status"><i className='bx bx-cog'></i></div>
            //                  </div>
            //             </div>
    
            //             <div className="role">
            //                 <div className="role-info">
            //                     <div className="role-color"></div>
            //                     <div className="role-name">Название роли</div>
            //                 </div>
            //                  <div className="role-info2">
            //                     <!-- <div className="count"><i className='bx bxs-user'></i> <div className="num">4</div></div> -->
            //                     <div className="status"><i className='bx bx-cog'></i></div>
            //                  </div>
            //             </div>
    
            //         </div>
            //     </div>
            // </div> */}
        </div>
    </div>
    );
}